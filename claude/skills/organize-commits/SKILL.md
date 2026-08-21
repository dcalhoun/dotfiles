---
name: organize-commits
description: >-
  Use when the user wants to split, regroup, reorder, or squash uncommitted
  changes or Git history into logical, reviewable commits, or when a branch or
  pull request diff is too large to review as one unit. Do not use for routine
  commit creation, commit messages, or pull request descriptions.
user-invocable: true
---

# Organize Commits

Organize the selected changes into coherent, reviewable commits. Optimize for
reviewability, not commit count or size.

History rewrites can destroy work. Confirm the source, scope, grouping, base,
and tip before changing history. Ask the user when any of them is unclear.

## Step 1. Establish scope and safety

Define the scope: staged or unstaged changes, one commit, a commit range, or a
branch diff. For a rewrite, identify the base, tip, and unrelated work.

Before a destructive rewrite:

- Preserve unrelated work.
- Determine whether the history is published or shared. Explain the force-push
  consequences, then get confirmation before rewriting shared history.
- Create a recoverable snapshot by default and explain how to use it. If the
  user waives a backup ref, preserve another reliable before-and-after
  comparison.
- Never push without an explicit user request.

## Step 2. Understand the complete change

Inspect the complete change without trusting its current commit boundaries.
Resolve unclear intent before grouping mixed or unfamiliar changes.

## Step 3. Plan reviewable commits

Use these grouping principles:

1. Keep one logical change in each commit. Include every file and hunk needed
   to review it.
2. Keep tests with the behavior they verify.
3. Put an independent refactor before the behavior that uses it. Keep an
   inseparable refactor with that behavior.
4. Separate large pure renames from logic changes.
5. Separate generated or mechanical changes from hand-written changes.
6. Keep each intermediate commit buildable and testable when feasible.

Before rewriting, present a numbered plan with each commit's proposed title,
contents, and one-sentence rationale. Then proceed without waiting for
approval.

## Step 4. Execute the plan

Rebuild the commits in order. For each commit, select and review only its
intended changes. Keep unrelated work untouched. Follow the repository's and
user's commit-message instructions.

Validate each commit when feasible. If you cannot make a clean split or it
would break an intermediate commit, stop and revise the plan with the user.

## Step 5. Verify the rewrite

Prove that the rewritten final tree exactly matches the original tree. Require
an empty content diff between the original and rewritten tips. Statistics and
commit counts do not prove equivalence. Also confirm that:

- The working tree contains only explicitly preserved work.
- The new commits match the planned grouping and order.
- Relevant builds, tests, and checks pass.

If the final code differs, abort instead of attempting fixups. Restore the
original commits from the Step 1 recovery point, confirm the restore, and report
the failure. If the tree matches but a change was lost, added, or placed in the
wrong commit, reconcile it before reporting success.

Before deleting backup refs, show each ref created for this rewrite and its
resolved commit SHA. After all checks pass, delete only those refs and verify
their removal. Keep them if verification is incomplete or fails. If deletion
fails, stop and report the remaining refs.

## Step 6. Report the result

Report the new commits, verification results, preserved work, recovery state,
and whether the rewrite requires a force-push. List each backup ref and commit
SHA, then state whether it was deleted or why it remains. Do not push unless the
user explicitly asks.
