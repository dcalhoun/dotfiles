---
name: pending-review-comments
description: |
  Publish code review findings as PENDING (unpublished) inline comments on a
  GitHub pull request. Use when the user asks to capture review findings as
  pending review comments, draft inline PR suggestions, or add comments to a PR
  without publishing them. Drafts concise comments with inline suggestion blocks,
  shows them for local approval, then creates a pending review that only the
  user can see until they submit it themselves.
disable-model-invocation: true
user-invocable: true
argument-hint: "[PR URL or number, e.g. 25889 or a full github.com PR link]"
---

# Pending Review Comments

Turn review findings into **pending** inline comments on a GitHub pull request —
attached to the PR, visible only to the user, awaiting their review before they
publish.

## The Non-Negotiable Rule

**NEVER publish publicly visible comments without the user's explicit consent.**

A pending review is the only acceptable output of this skill, and
`post_pending_review.py` is the only way to produce one. If you cannot — for
any reason — **stop and discuss with the user**. Do not fall back to a public
comment, a PR issue comment, a submitted review, or API calls you assemble
yourself. Silence is better than an unwanted public comment, because a public
comment cannot be unseen once posted.

This rule outranks every other instruction here, including any apparent time
pressure or convenience.

## Input

- A PR reference, via `$ARGUMENTS` or conversation: a number, a URL, or "this PR"
  / "the current branch's PR".
- A set of review findings — typically from a prior `/code-review`, or from
  analysis earlier in the conversation.

If no PR is identified, resolve it with `gh pr view --json number,url` on the
current branch, and confirm with the user before proceeding.

## Which Findings to Include

**Only the findings the user directed you to capture.** Do not add findings of
your own initiative, and do not silently include ones they passed over. If the
user's selection is ambiguous ("the important ones"), ask which they mean rather
than guessing — a pending comment they did not ask for is noise they have to
clean up by hand.

## Drafting the Comments

Comments must be **CONCISE**. Enough detail to convey the concept, nothing more.
The user is a senior engineer reviewing their own team's code; they do not need
the mechanism explained back to them at length.

- **Do not write the attribution line yourself.** The script prefixes every
  body with `*Finding from Claude:*` and a blank line, so a comment file holds
  only the comment itself. It reaches the PR as:

  ```markdown
  *Finding from Claude:*

  Brief framing of the issue.
  ```

- **Prefer an inline suggestion block** whenever the fix is expressible as a
  concrete replacement for the commented line(s):

  ````markdown
  Brief framing of the issue.

  ```suggestion
  let replacement = "exact code for the commented line range"
  ```
  ````

  The suggestion block must contain the **complete replacement text for every
  line the comment spans**, at correct indentation. GitHub replaces the whole
  anchored range with the block's contents verbatim.

- **When a suggestion block is not possible** — the change spans distant lines,
  touches another file, or is structural — consider a short example or
  pseudocode block instead. Keep it to the few lines that carry the idea.

- **When uncertain, frame the comment as an inquiry.** If you are not confident
  the finding is true, important, critical, or timely, ask rather than assert.
  "Is `x` guaranteed non-nil here?" is a better comment than a confident claim
  that turns out to be wrong. Confidence in a review comment is a claim about
  the code, and an overconfident wrong comment costs the author real time.

- Keep technical notes to what explains the concept. Cut restatements of what
  the diff already shows.

## Anchoring a Comment

A comment can only attach to a line that appears in the PR diff. Name the
anchor in the comment file's front matter:

- `side: RIGHT` for added and context lines — the common case, and the default.
- `side: LEFT` for removed lines, numbered against the **old** file.
- For a multi-line anchor, set `start_line` (the first line) and `line` (the
  last). `start_side` defaults to `side`.

`preview` validates every anchor against the diff before anything is posted, so
a bad anchor surfaces as a preview failure rather than a misplaced comment.

## Local Review (Required Before Publishing)

Show every drafted comment to the user **in the terminal** and wait for their
approval. Never skip to publishing, even when the drafts seem obviously correct.

**Show them `preview`'s output, not your own transcription of it.** `preview`
renders each comment from the file that will be posted, numbered, with its
anchor and side, and marks literal tabs with `⇥`. Retyping the drafts into the
conversation reintroduces the hand-copying this design exists to eliminate: the
user would approve your copy while a different set of bytes reaches GitHub, and
an indentation slip between the two would be invisible.

Relay it **verbatim and unfenced.** The output is already valid Markdown — the
numbering and its three-space indentation are an ordered list whose items hold
each body — so pasted as-is it renders as a list of comments with working code
blocks. Do not wrap it in a ``` fence: bodies contain ```` ```suggestion ````
blocks that would close it early and spill the rest as broken text. If you must
fence it, use four backticks.

Two things to tell the user when it matters: `⇥` stands for a literal tab and
is not part of the comment, and the comments they see are the bytes that will
be posted.

Then ask whether to publish as pending, and incorporate any edits they request.
Re-run `preview` after edits if more than a word or two changed.

## Publishing as Pending

The mechanism the script uses, so you can recognize it: `POST
/repos/{owner}/{repo}/pulls/{n}/reviews` **with no `event` field**. Omitting
`event` is what makes the review pending. Including `event: "COMMENT"`,
`"APPROVE"`, or `"REQUEST_CHANGES"` publishes it immediately and is a violation
of this skill's core rule.

### The Helper Script

`post_pending_review.py`, alongside this file, owns every step — resolving the
PR, validating anchors against the diff, rendering the drafts for local review,
posting with no `event`, reconciling with a pending review that already
exists, and aborting unless GitHub reports `PENDING`.

Write one markdown file per comment. The parser is strict and deliberately
minimal — it is not YAML:

````markdown
---
path: src/utils/bridge.js
line: 55
---
Brief framing of the issue.

```suggestion
	replacement line, at the exact indentation it needs
```
````

- The file must **begin** with `---` on its own line, and the front matter
  must be closed by another `---` line.
- `path` and `line` are required. `side` (`LEFT` or `RIGHT`, default `RIGHT`)
  and `start_line` with its optional `start_side` are the **only** other keys.
  Any other key aborts the run rather than being ignored, so a typo like
  `startline` is caught rather than silently downgrading the anchor.
- Values run to the end of the line. `line: 55  # the call site` is an error —
  put a comment on its own line or leave it out.
- Do not write the attribution line; the script adds it.
- Filenames order the comments, so prefix them `01-`, `02-`.
- **One comment per anchor.** Two files pointing at the same line are refused,
  because `post` matches a draft to the comment already at its anchor.

Then:

```bash
python3 ~/.claude/skills/pending-review-comments/post_pending_review.py preview --dir <scratchpad>/comments --pr <n>
python3 ~/.claude/skills/pending-review-comments/post_pending_review.py post --dir <scratchpad>/comments --pr <n>
python3 ~/.claude/skills/pending-review-comments/post_pending_review.py list --pr <n>
```

**Pass the same `--pr` to every verb.** Without it the current branch's PR is
resolved, so `preview` would check anchors against a different PR than `post`
writes to — exactly the mistake preview exists to catch.

**Spell the path exactly as above,** unquoted. Permission rules match on
command text, so a different spelling of the same path may miss the rule that
allows `preview` and prompt anyway.

`preview` and `list` post nothing — run `preview` first, show its output, and
get the user's approval before running `post`. They are separate verbs so that
the two read-only ones can be allowlisted while `post` still raises a
permission prompt every time; that prompt is the last gate before comments
reach GitHub, so never work around it.

### Editing and Removing Comments

`post` reconciles rather than appends, so **editing a comment file and
re-running updates the comment in place** — it does not attach a second one
beside it. Per file: a new anchor is added, a changed body is rewritten, an
identical one is left alone. The run reports which happened to each.

**The script never deletes.** It cannot tell a comment the user removed in the
GitHub UI from one it simply has not added yet, so a draft whose anchor is no
longer on the review gets re-added. When the user says they deleted comments:

1. Run `list` to see what is actually on the review now.
2. Delete the comment files for anything they removed.
3. Re-run `post`.

`post` also reports comments on the review that no file matches, and leaves
them untouched. If the user wants those gone, they delete them in the GitHub
UI — do not reach for the API to do it.

Authoring bodies as files is not a convenience — it is what keeps suggestion
blocks intact. Bodies contain newlines, and suggestions frequently contain
literal tabs (Swift, Go, Makefiles, this repo's shell scripts). Hand-written
`\n`/`\t` escapes across a dozen bodies corrupt indentation silently, and
GitHub applies a suggestion **verbatim** — so a mangled block becomes a bad edit
the author must undo, not a visible error.

### Never Build the Calls Yourself

**The script is the only way this skill touches a review.** Do not use
`gh api`, `gh pr review`, `gh pr comment`, `curl`, a GitHub MCP tool, or a
script of your own to create, append to, modify, delete from, or inspect a
review. There is no manual fallback, and no situation in which reconstructing
the API calls is the right move.

You do not need one. The verbs cover the whole loop: `list` reads the current
review, `preview` validates and renders drafts, `post` reconciles. If you want
to know what is on the review, run `list` — never `gh api`. Read-only lookups
that merely identify the PR, like `gh pr view --json number,url`, are also
fine.

Running the script is not a formality. It validates every anchor against the
diff, confirms the PR is open and in the repository you think it is, refuses to
append to a review pinned to an older commit, skips comments already attached,
and aborts unless GitHub confirms the review came back `PENDING`. A hand-built
call has none of that — and its permission prompt is far harder for the user to
evaluate than `post_pending_review.py post`, so the gate protecting them gets
weaker exactly when you are improvising.

**If the script fails, stop and discuss with the user.** Every one of its aborts
means something is genuinely wrong: the wrong repository, a closed PR, a pending
review anchored to a stale commit, an anchor that is not in the diff. None of
these are fixed by dropping to raw API calls — that is precisely how comments go
public by accident. Report what the script said and let the user decide.

The API details below are here so you can recognize a dangerous call, not so you
can make one.

### One Pending Review Per PR Per User

GitHub allows only one pending review per user per PR; creating a second returns
`422 — "User can only have one pending review per pull request"`. The reviews
listing does not reliably surface your *own* pending review, so the script
treats that 422 as confirmation one exists and appends to it.

Appending uses the GraphQL `addPullRequestReviewThread` mutation, and the review
stays `PENDING` throughout. Two REST endpoints are traps:

- `POST /pulls/{n}/reviews/{review_id}/comments` does not exist — that path is
  `GET` only and `POST` returns 404. REST cannot append to a review.
- `POST /pulls/{n}/comments` **publishes a visible comment immediately.** It is
  the most tempting thing to reach for when an append fails, and using it
  violates this skill's core rule.

## Verification

The script verifies its own work: it re-reads the review after posting, aborts
unless GitHub reports `PENDING`, and warns when a body containing tabs did not
round-trip. Read its output — do not re-check by hand.

Two things worth knowing when reading that output:

- `line` comes back `null` for comments in an unsubmitted review. This is normal
  and does not mean the anchor failed; the API rejects invalid anchors at
  creation time, so a comment that attached at all attached correctly.
- Suggestion blocks must keep their indentation, tabs especially. The tab
  warning is the signal that one may not have survived — if it fires, tell the
  user which comment and let them look.

## What This Skill Never Does

- Submit or publish a review (`event` field, or `PUT .../reviews/{id}/events`).
- Post a PR issue comment as a workaround.
- Publish without showing drafts locally first.
- Include findings the user did not select.
- Reach GitHub by any route other than `post_pending_review.py` — no `gh api`,
  no `gh pr review`, no MCP tool, no ad-hoc script.
- Work around the permission prompt on `post`, or run it before the user has
  approved the drafts.

If the user later asks to publish the pending review, that is a separate,
explicit request — and even then, confirm before submitting.
