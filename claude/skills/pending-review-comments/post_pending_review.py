#!/usr/bin/env python3
"""Post review findings to a GitHub PR as a PENDING review.

Comments are authored as individual markdown files so that bodies — which
contain newlines, and suggestion blocks that often contain literal tabs —
never pass through hand-written JSON escapes. GitHub applies a suggestion
verbatim, so corrupted indentation becomes a bad edit rather than a visible
error.

Each comment file carries front matter naming its anchor:

    ---
    path: test/ios/run.sh
    line: 33
    ---
    Body text. Real tabs. Real newlines.

`path` and `line` are required. `side` (LEFT or RIGHT, default RIGHT) and
`start_line` with its optional `start_side` are the only other keys; anything
else is rejected rather than ignored. Values run to the end of the line, so a
trailing `#` comment becomes part of the value — put comments on their own
line.

Files are ordered by filename, so a `01-`, `02-` prefix controls the order
they are posted in. One comment per anchor: `post` matches a draft to the
comment already at its anchor, so two drafts on the same line are refused.

    S=~/.claude/skills/pending-review-comments/post_pending_review.py
    python3 $S preview --dir ./comments --pr 82565
    python3 $S post    --dir ./comments --pr 82565
    python3 $S list                     --pr 82565

Pass the same --pr to every verb; without it the current branch's PR is
resolved, so preview would check anchors against a different PR than post
writes to.

`post` reconciles rather than appends. A draft whose anchor is new is added,
one whose body changed is rewritten in place, and one that already matches is
left alone — so editing a comment file and re-running updates the comment
instead of attaching a second one beside it. Comments on the review with no
matching file are reported and left untouched; `list` shows what is there.

SAFETY: this script has no code path that submits a review. The create call
never sends an `event` field, and the run aborts unless GitHub reports the
review as PENDING. Publishing stays a human action in the GitHub UI.

`post` is a separate verb rather than a flag so a permission rule can allow
`preview` and `list` outright while still prompting for anything that writes
to GitHub.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

ATTRIBUTION = "*Finding from Claude:*"
GH_TIMEOUT = 120
SIDES = ("LEFT", "RIGHT")
KEYS = {"path", "line", "start_line", "side", "start_side"}


# --- shelling out to gh ------------------------------------------------------


def cmd_summary(cmd):
    """A command line fit for an error message.

    GraphQL arguments carry whole comment bodies and the mutation source, so
    an unabridged command buries the actual error under screens of text.
    """
    return " ".join(a if len(a) <= 60 else a[:57] + "..." for a in cmd)


class GhError(RuntimeError):
    """A `gh` invocation that exited non-zero."""

    def __init__(self, cmd, stdout, stderr):
        # gh puts its own summary on stderr but the API's error body — the
        # part naming what actually went wrong — on stdout. Callers matching
        # on a message, and users reading the failure, need both.
        self.stdout = stdout
        self.stderr = stderr
        self.output = "\n".join(part for part in (stderr, stdout) if part)
        super().__init__(f"gh failed: {cmd_summary(cmd)}\n{self.output}")


def gh(args, payload=None, payload_dir=None):
    """Run `gh` and return parsed JSON stdout (or None when empty)."""
    cmd = ["gh"] + args
    tmp = None
    try:
        if payload is not None:
            # Alongside the comment files, so the payload stays in the
            # caller's scratchpad rather than landing in $TMPDIR.
            with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False, dir=payload_dir
            ) as fh:
                tmp = fh.name
                json.dump(payload, fh)
            cmd += ["--input", tmp]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=GH_TIMEOUT
            )
        except FileNotFoundError:
            sys.exit("gh is not on PATH — install the GitHub CLI.")
        except subprocess.TimeoutExpired:
            sys.exit(f"gh timed out after {GH_TIMEOUT}s: {cmd_summary(cmd)}")
    finally:
        if tmp:
            Path(tmp).unlink(missing_ok=True)

    if proc.returncode != 0:
        raise GhError(cmd, proc.stdout.strip(), proc.stderr.strip())
    out = proc.stdout.strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        sys.exit(f"gh returned output that is not JSON: {cmd_summary(cmd)}\n{out[:500]}")


# --- comment files -----------------------------------------------------------


def parse_int(path, meta, key):
    try:
        return int(meta[key])
    except ValueError:
        sys.exit(f"{path}: '{key}' must be a whole number, got {meta[key]!r}")


def parse_side(path, meta, key, default):
    side = meta.get(key, default)
    if side not in SIDES:
        sys.exit(f"{path}: '{key}' must be LEFT or RIGHT, got {side!r}")
    return side


def parse_comment_file(path):
    """Parse front matter + body. Deliberately minimal: no YAML dependency."""
    text = path.read_text()
    if not text.startswith("---\n"):
        sys.exit(f"{path}: must begin with '---' front matter")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        sys.exit(f"{path}: front matter is not closed by a '---' line")
    _, front, body = parts

    meta = {}
    for raw in front.strip().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            sys.exit(f"{path}: cannot parse front matter line: {raw!r}")
        key, _, value = raw.partition(":")
        meta[key.strip()] = value.strip()

    if "path" not in meta or "line" not in meta:
        sys.exit(f"{path}: front matter needs at least 'path' and 'line'")

    # A typo in an optional key would otherwise be dropped in silence, and
    # `line`/`side` are exactly the fields a silent default gets wrong.
    unknown = sorted(set(meta) - KEYS)
    if unknown:
        sys.exit(f"{path}: unknown front matter key(s): {', '.join(unknown)}")

    body = body.strip("\n")
    if body.startswith(ATTRIBUTION):
        body = body[len(ATTRIBUTION):].strip("\n")
    if not body.strip():
        sys.exit(f"{path}: body is empty")

    comment = {
        "path": meta["path"],
        "line": parse_int(path, meta, "line"),
        "side": parse_side(path, meta, "side", "RIGHT"),
        "body": f"{ATTRIBUTION}\n\n{body}",
    }
    if "start_line" in meta:
        comment["start_line"] = parse_int(path, meta, "start_line")
        comment["start_side"] = parse_side(path, meta, "start_side", comment["side"])
    return comment


def load_comments(directory):
    files = sorted(Path(directory).glob("*.md"))
    if not files:
        sys.exit(f"no .md comment files in {directory}")
    return [(f, parse_comment_file(f)) for f in files]


# --- anchor validation -------------------------------------------------------


HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def diff_lines(patch):
    """Line numbers addressable on each side of a unified diff patch."""
    right, left = set(), set()
    new_no = old_no = 0
    for line in (patch or "").splitlines():
        m = HUNK.match(line)
        if m:
            old_no, new_no = int(m.group(1)), int(m.group(2))
            continue
        if line.startswith("+"):
            right.add(new_no)
            new_no += 1
        elif line.startswith("-"):
            left.add(old_no)
            old_no += 1
        elif line.startswith(" ") or not line:
            # A blank context line is a lone space, which anything that trims
            # trailing whitespace turns into an empty string. Counting it as
            # context either way keeps the rest of the hunk in step.
            right.add(new_no)
            left.add(old_no)
            new_no += 1
            old_no += 1
    return right, left


def validate(repo, number, comments):
    files = gh(["api", f"repos/{repo}/pulls/{number}/files", "--paginate"])
    patches = {f["filename"]: f.get("patch") for f in files}

    problems, seen = [], {}
    for source, c in comments:
        if "start_line" in c and c["start_line"] >= c["line"]:
            problems.append(
                f"{source.name}: start_line {c['start_line']} must come before "
                f"line {c['line']}"
            )
        # One comment per anchor: reconciliation matches on the anchor, so two
        # drafts sharing one cannot be told apart on a later run.
        if anchor(c) in seen:
            problems.append(
                f"{source.name}: anchors {c['path']}:{c['line']}, which "
                f"{seen[anchor(c)]} already uses"
            )
        seen[anchor(c)] = source.name

        if c["path"] not in patches:
            problems.append(f"{source.name}: {c['path']} is not in this PR")
            continue
        if patches[c["path"]] is None:
            # Binary, renamed and very large files come back without a patch.
            # Posting an anchor nobody could check would quietly break the
            # guarantee that a bad anchor fails in preview.
            problems.append(
                f"{source.name}: {c['path']} has no patch in the API response, "
                "so its anchor cannot be verified"
            )
            continue
        right, left = diff_lines(patches[c["path"]])
        addressable = {"RIGHT": right, "LEFT": left}
        for key, side_key in (("start_line", "start_side"), ("line", "side")):
            if key in c and c[key] not in addressable[c[side_key]]:
                problems.append(
                    f"{source.name}: {c['path']}:{c[key]} "
                    f"is not on the {c[side_key]} side of the diff"
                )
    if problems:
        sys.exit("Anchor validation failed:\n  " + "\n  ".join(problems))


# --- posting -----------------------------------------------------------------


PENDING_REVIEW_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  viewer { login }
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviews(first: 20, states: PENDING) {
        nodes { id databaseId commit { oid } author { login } }
      }
    }
  }
}"""


def find_pending(repo, number):
    """Locate the viewer's pending review, if any.

    The REST reviews listing does not reliably surface your *own* pending
    review — that is why creation can still 422 after a lookup finds nothing.
    GraphQL reports it directly, on the same API surface the append uses.
    """
    owner, _, name = repo.partition("/")
    data = gh([
        "api", "graphql",
        "-f", f"query={PENDING_REVIEW_QUERY}",
        "-f", f"owner={owner}",
        "-f", f"name={name}",
        "-F", f"number={number}",
    ])["data"]
    login = data["viewer"]["login"]
    for node in data["repository"]["pullRequest"]["reviews"]["nodes"]:
        if (node.get("author") or {}).get("login") == login:
            return {
                "id": node["databaseId"],
                "node_id": node["id"],
                "commit_id": (node.get("commit") or {}).get("oid"),
            }
    return None


def create_review(repo, number, head_sha, comments, payload_dir):
    # No `event` key: omitting it is what makes the review pending.
    payload = {"commit_id": head_sha, "comments": [c for _, c in comments]}
    return gh(
        ["api", f"repos/{repo}/pulls/{number}/reviews", "--method", "POST"],
        payload=payload,
        payload_dir=payload_dir,
    )


REVIEW_COMMENTS_QUERY = """
query($id: ID!, $cursor: String) {
  node(id: $id) {
    ... on PullRequestReview {
      comments(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { id path line startLine body }
      }
    }
  }
}"""


def review_comments(review_node_id):
    """Comments already attached to a review.

    Read over GraphQL because REST reports `line: null` for an unsubmitted
    review, which leaves its anchors unusable for matching.
    """
    out, cursor = [], None
    while True:
        args = ["api", "graphql", "-f", f"query={REVIEW_COMMENTS_QUERY}",
                "-f", f"id={review_node_id}"]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        conn = gh(args)["data"]["node"]["comments"]
        out += conn["nodes"]
        if not conn["pageInfo"]["hasNextPage"]:
            return out
        cursor = conn["pageInfo"]["endCursor"]


def anchor(c):
    """Where a drafted comment attaches — its identity on the review."""
    return (c["path"], c["line"], c.get("start_line"))


def posted_anchor(c):
    """The same identity, as GraphQL spells it."""
    return (c["path"], c["line"], c["startLine"])


ADD_THREAD = """
mutation($r: ID!, $path: String!, $body: String!, $line: Int!,
         $side: DiffSide!, $startLine: Int, $startSide: DiffSide) {
  addPullRequestReviewThread(input: {
    pullRequestReviewId: $r, path: $path, body: $body, line: $line,
    side: $side, startLine: $startLine, startSide: $startSide
  }) { thread { comments(first: 1) { nodes { databaseId } } } }
}"""

UPDATE_COMMENT = """
mutation($id: ID!, $body: String!) {
  updatePullRequestReviewComment(input: {
    pullRequestReviewCommentId: $id, body: $body
  }) { pullRequestReviewComment { state } }
}"""


def add_thread(review, c):
    """REST has no endpoint for this; GraphQL addPullRequestReviewThread does."""
    args = [
        "api", "graphql", "-f", f"query={ADD_THREAD}",
        "-f", f"r={review['node_id']}",
        "-f", f"path={c['path']}",
        "-f", f"body={c['body']}",
        "-F", f"line={c['line']}",
        "-F", f"side={c['side']}",
    ]
    if "start_line" in c:
        args += ["-F", f"startLine={c['start_line']}",
                 "-F", f"startSide={c['start_side']}"]
    gh(args)


def update_comment(comment_node_id, body):
    """Rewrite a comment in place. The review stays PENDING through it."""
    gh(["api", "graphql", "-f", f"query={UPDATE_COMMENT}",
        "-f", f"id={comment_node_id}", "-f", f"body={body}"])


def sync_review(review, comments):
    """Bring an existing pending review in line with the drafted files.

    Matching is by anchor rather than by body, so a reworded draft rewrites
    the comment already at that anchor instead of attaching a second one
    beside it. Body-matching could not tell an edit from a new finding.
    """
    posted = review_comments(review["node_id"])
    at = {}
    for c in posted:
        at.setdefault(posted_anchor(c), []).append(c)

    added = updated = unchanged = 0
    for source, c in comments:
        here = at.get(anchor(c), [])
        if len(here) > 1:
            sys.exit(
                f"ABORT: review {review['id']} already holds {len(here)} "
                f"comments at {c['path']}:{c['line']}, so {source.name} cannot "
                "be matched to one of them. Resolve that anchor by hand."
            )
        try:
            if not here:
                add_thread(review, c)
                added += 1
                print(f"   added    {source.name}")
            elif here[0]["body"] == c["body"]:
                unchanged += 1
                print(f"   unchanged {source.name}")
            else:
                update_comment(here[0]["id"], c["body"])
                updated += 1
                print(f"   updated  {source.name}")
        except (GhError, SystemExit):
            # Each call stands on its own with no rollback, so say what landed
            # before the failure propagates and takes the closing report away.
            print(f"\nFailed on {source.name}. This run already added {added} "
                  f"and updated {updated} comment(s) on review {review['id']}; "
                  "re-running resumes from here.")
            raise

    extra = [c for c in posted if posted_anchor(c) not in
             {anchor(c) for _, c in comments}]
    if extra:
        print(f"\n{len(extra)} comment(s) on the review are not in this "
              "directory — left untouched:")
        for c in extra:
            span = f"{c['startLine']}-{c['line']}" if c["startLine"] else c["line"]
            print(f"   {c['path']}:{span}")

    return added, updated, unchanged


# --- output ------------------------------------------------------------------


def show_indent(line):
    """Make every literal tab visible.

    A terminal draws a tab and a run of spaces identically, so the reviewer
    approving a suggestion block cannot otherwise see which one it carries —
    and GitHub applies the block verbatim. Mixed space-then-tab indentation is
    the case worth catching, so mark tabs wherever they fall.
    """
    return line.replace("\t", "⇥")


def render(comments):
    for i, (source, c) in enumerate(comments, 1):
        span = c["path"] + ":"
        span += f"{c['start_line']}-{c['line']}" if "start_line" in c else str(c["line"])
        # Two trailing spaces are a Markdown hard break: the agent relays this
        # output verbatim, so it has to render as well as it reads.
        print(f"\n{i}. **{source.stem}**  ")
        print(f"   `{span}`  ({c['side']})\n")
        for line in c["body"].splitlines():
            print(f"   {show_indent(line)}" if line else "")
    if any("\t" in c["body"] for _, c in comments):
        print("\n⇥ marks a literal tab. It posts as a tab, not as that glyph.")


def resolve_pr(pr_ref, repo_hint):
    """Resolve the PR, taking its repository from the URL it reports.

    The PR's own URL is the authority on which repository it belongs to, so
    every identifier comes from one `gh pr view`. Deriving the repo from the
    working directory instead would let a `--pr` URL validate against one PR
    and post to a same-numbered PR somewhere else.
    """
    view = ["pr", "view", "--json", "number,headRefOid,url,state"]
    if pr_ref:
        view.insert(2, pr_ref)
    if repo_hint:
        view += ["--repo", repo_hint]
    pr = gh(view)

    parts = urlparse(pr["url"]).path.split("/")
    if len(parts) < 5 or parts[3] != "pull":
        sys.exit(f"cannot read a repository from the PR url {pr['url']}")
    repo = f"{parts[1]}/{parts[2]}"
    return repo, pr["number"], pr["headRefOid"], pr["url"], pr["state"]


def show_review(repo, number, url):
    """Print what is currently on the pending review, and post nothing."""
    existing = find_pending(repo, number)
    if existing is None:
        print(f"No pending review on {repo}#{number}.")
        return
    posted = review_comments(existing["node_id"])
    print(f"PENDING review {existing['id']} on {repo}#{number} — "
          f"{len(posted)} comment(s):\n")
    for i, c in enumerate(posted, 1):
        span = f"{c['startLine']}-{c['line']}" if c["startLine"] else c["line"]
        print(f"{i}. `{c['path']}:{span}`\n")
        for line in c["body"].splitlines():
            print(f"   {show_indent(line)}" if line else "")
        print()
    print(f"Review them under Files changed: {url}/files")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("mode", choices=("preview", "post", "list"),
                    help="preview: validate anchors and render the drafts, "
                         "posting nothing. post: reconcile the pending review "
                         "with them. list: show what is on the review now")
    ap.add_argument("--dir", help="directory of .md comment files "
                                  "(required for preview and post)")
    ap.add_argument("--pr", help="PR number or URL (default: current branch's PR)")
    ap.add_argument("--repo", help="owner/name, to resolve a bare --pr number "
                                   "from outside that repository's clone")
    args = ap.parse_args()

    if args.mode != "list" and not args.dir:
        ap.error("--dir is required for preview and post")

    repo, number, head_sha, url, state = resolve_pr(args.pr, args.repo)

    if args.mode == "list":
        show_review(repo, number, url)
        return

    if state != "OPEN":
        sys.exit(f"{repo}#{number} is {state}, not open.")

    comments = load_comments(args.dir)
    validate(repo, number, comments)
    render(comments)
    print(f"\n{len(comments)} comment(s) for {repo}#{number} @ {head_sha[:9]}")

    if args.mode == "preview":
        print("\nPreview — nothing posted.")
        return

    existing = find_pending(repo, number)
    review_id = review_node = attached = None

    if existing is None:
        try:
            review = create_review(repo, number, head_sha, comments, Path(args.dir))
        except GhError as err:
            # Belt and braces: the lookup above should have found it, so a 422
            # here means GitHub disagrees. Trust the 422 and look again.
            if "one pending review" not in err.output:
                raise
            print("\nGitHub reports an existing pending review; re-resolving it.")
            existing = find_pending(repo, number)
            if existing is None:
                sys.exit(
                    "ABORT: GitHub reports a pending review the API will not "
                    f"list. Resolve it by hand: {url}/files"
                )
        else:
            review_id, review_node = review["id"], review["node_id"]
            attached = f"{len(comments)} added"
            if review["state"] != "PENDING":
                sys.exit(
                    f"ABORT: review {review_id} came back {review['state']}, "
                    "not PENDING. Comments may be publicly visible — check the "
                    "PR now."
                )

    if existing is not None:
        # Anchors were validated against the PR head. A review pinned to an
        # older commit would attach them to whatever those lines are now.
        if existing.get("commit_id") not in (None, head_sha):
            sys.exit(
                f"ABORT: pending review {existing['id']} anchors to "
                f"{existing['commit_id'][:9]}, but the PR head is "
                f"{head_sha[:9]}. Submit or discard that review first."
            )
        print(f"\nReconciling with pending review {existing['id']}.")
        review_id, review_node = existing["id"], existing["node_id"]
        added, updated, unchanged = sync_review(existing, comments)
        attached = f"{added} added, {updated} updated, {unchanged} unchanged"

    posted = review_comments(review_node)
    review_state = gh(
        ["api", f"repos/{repo}/pulls/{number}/reviews/{review_id}"])["state"]
    if review_state != "PENDING":
        sys.exit(f"ABORT: review {review_id} is {review_state}, not PENDING. "
                 "Check the PR now.")

    # One check, on the same anchor-plus-body the sync just wrote: every draft
    # must be on the review with exactly the body drafted for it. A dropped
    # comment and a mangled one both land here.
    stored = {posted_anchor(c): c["body"] for c in posted}
    wrong = [s.name for s, c in comments if stored.get(anchor(c)) != c["body"]]
    if wrong:
        sys.exit(
            f"ABORT: review {review_id} does not match {len(wrong)} of "
            f"{len(comments)} drafted comment(s): {', '.join(wrong)}. "
            f"Check the review before adding anything else: {url}/files"
        )

    print(f"\nPENDING review {review_id} — {attached}; "
          f"{len(posted)} comment(s) in the review.")
    print(f"Review them under Files changed: {url}/files")
    print("Submitting is yours; this script never publishes.")


if __name__ == "__main__":
    try:
        main()
    except GhError as err:
        sys.exit(str(err))
