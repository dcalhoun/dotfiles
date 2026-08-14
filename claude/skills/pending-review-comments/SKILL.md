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

A pending review is the only acceptable output of this skill. If you cannot
create one — for any reason — **stop and discuss with the user**. Do not fall
back to a public comment, a PR issue comment, or a submitted review. Silence is
better than an unwanted public comment, because a public comment cannot be
unseen once posted.

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

## Local Review (Required Before Publishing)

Show every drafted comment to the user **in the terminal** and wait for their
approval. Never skip to publishing, even when the drafts seem obviously correct.

Display as a list, one entry per comment:

```
1. **Brief subject title**
   `path/to/File.swift:60`

   <the exact draft comment body, rendered as it will appear>
```

Then ask whether to publish as pending, and incorporate any edits they request.
Re-display after edits if more than a word or two changed.

## Publishing as Pending

The mechanism: `POST /repos/{owner}/{repo}/pulls/{n}/reviews` **with no `event`
field**. Omitting `event` is what makes the review pending. Including
`event: "COMMENT"`, `"APPROVE"`, or `"REQUEST_CHANGES"` publishes it immediately
and is a violation of this skill's core rule.

### Steps

1. Get the head SHA — comments must anchor to the commit under review:

   ```bash
   gh pr view <n> --repo <owner>/<repo> --json headRefOid,title,state
   ```

2. Confirm the target lines are valid. A comment can only anchor to a line that
   appears in the diff. Inspect the patch:

   ```bash
   gh api repos/<owner>/<repo>/pulls/<n>/files \
     --jq '.[] | select(.filename=="<path>") | .patch'
   ```

   Use `side: "RIGHT"` for added/context lines (the common case) and
   `side: "LEFT"` for removed lines. For a multi-line comment, set `start_line`
   plus `line` (the end), both on the same side.

3. Write the payload to a file in the scratchpad directory (not `/tmp`) and post
   it. Using `--input` avoids shell-quoting problems with multi-line bodies:

   ```bash
   gh api repos/<owner>/<repo>/pulls/<n>/reviews \
     --method POST --input <scratchpad>/review.json \
     --jq '{id, state, user: .user.login}'
   ```

   Payload shape:

   ````json
   {
     "commit_id": "<headRefOid>",
     "comments": [
       {
         "path": "path/to/File.swift",
         "line": 60,
         "side": "RIGHT",
         "body": "Comment text.\n\n```suggestion\n    replacement\n```"
       }
     ]
   }
   ````

4. **Verify the result is pending.** The response must show `"state": "PENDING"`.
   If it shows anything else, tell the user immediately and plainly — a
   non-pending state means comments went public, and they need to know at once so
   they can decide whether to delete them.

5. Report back: the review ID, the pending state, and where to find the comments
   (the PR's **Files changed** tab). Remind them the submit step is theirs.

### One Pending Review Per PR Per User

GitHub allows only one pending review per user per PR. If one already exists,
creating another fails. Append to the existing review instead:

```bash
gh api repos/<owner>/<repo>/pulls/<n>/reviews/<review_id>/comments \
  --method POST --input <scratchpad>/comment.json
```

Find an existing pending review with:

```bash
gh api repos/<owner>/<repo>/pulls/<n>/reviews \
  --jq '.[] | select(.state=="PENDING") | {id, user: .user.login}'
```

Note this endpoint is unreliable for surfacing _your own_ pending review in some
cases; treat a creation failure mentioning an existing review as confirmation
that one is there, and append rather than retrying.

## Verification

After publishing, confirm the comments attached:

```bash
gh api repos/<owner>/<repo>/pulls/<n>/reviews/<review_id>/comments \
  --jq '.[] | {path, line, body}'
```

`line` may come back `null` for comments in an unsubmitted review — this is
normal and does not mean the anchor failed. The API rejects invalid anchors at
creation time, so a successful `POST` means the lines were accepted.

## What This Skill Never Does

- Submit or publish a review (`event` field, or `PUT .../reviews/{id}/events`).
- Post a PR issue comment as a workaround.
- Publish without showing drafts locally first.
- Include findings the user did not select.

If the user later asks to publish the pending review, that is a separate,
explicit request — and even then, confirm before submitting.
