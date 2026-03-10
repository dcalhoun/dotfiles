---
name: weekly-update
description: |
  Draft a weekly update for the sprint P2 post. Use when the user asks
  to write, draft, or prepare a weekly update. Gathers Linear issues, GitHub PRs,
  Slack activity, and enterprise GitHub A8C activity, then drafts an
  update following the team's established format and preferences.
disable-model-invocation: true
user-invocable: true
argument-hint: "[date-range, e.g. Mar 3 – Mar 9]"
---

# Weekly Update Skill

Draft a weekly update for the sprint P2 post.

## Input

The user provides:

- A date range for the update (e.g., "Mar 3 – Mar 9"), either as `$ARGUMENTS` or in conversation.

If no date range is provided, ask the user.

## Data Gathering

Use the ContextA8C MCP server to gather activity from all of the following sources. Load each provider first, then execute the relevant tools. Run independent queries in parallel when possible.

### 1. Linear Issues

- Fetch issues assigned to the user updated during the date range (`my-issues` with appropriate `days` filter).
- Categorize into: completed, in progress, and needs review.
- Note: some issues may have been completed in prior weeks but only status-updated during this range. Cross-reference with the user's previous weekly updates if available.

### 2. GitHub PRs (github.com)

- Search for PRs authored by `dcalhoun` created or merged during the date range.
- Search for PRs reviewed by `dcalhoun` updated during the date range (for the Misc line).
- Count Dependabot dependency version bump PRs merged in GutenbergKit during the date range.

### 3. Enterprise GitHub A8C PRs

- Search for PRs authored by `davidcalhoun` created or merged during the date range.
- Search for PRs reviewed by `davidcalhoun` updated during the date range.

### 4. Slack Activity

- Search for messages sent by the user (`from:me`) during the date range.
- Look for noteworthy work discussions, coordination, or announcements that may not be captured in Linear or GitHub.

### 5. P2 Activity

- Search for P2 posts and comments by the user during the date range.
- Look for noteworthy discussions, technical write-ups, or announcements that may not be captured in Linear or GitHub.

## Formatting Rules

Follow these rules exactly when drafting the update:

### Structure

```
**Days worked last week:** [number]

**Planned time off this week:** [None or details]

**Work completed last week:**

- [bullet items]

**Commitments this week:**

- [bullet items]

**Something fun:** [PLACEHOLDER]
```

### References

- Prefer Linear issue IDs/URLs as references (e.g., `[CMM-1234](https://linear.app/a8c/issue/CMM-1234)`).
- Only use GitHub PR IDs/URLs or Slack thread URLs when no corresponding Linear issue exists (e.g., `[GBK #123](https://github.com/wordpress-mobile/GutenbergKit/pull/123)`).
- Never include both a Linear ID and a GitHub PR for the same item.

### Naming

- First mention of GutenbergKit should define the acronym: "GutenbergKit (GBK)".
- All subsequent references should use "GBK".

### Misc Line

Consolidate the following into a single bullet prefixed with "Misc:":

- PR reviews (mention which repos)
- Dependabot dependency version bump PRs merged (include count)
- App store review monitoring
- Other minor/routine work

Example: `Misc: reviewed teammate PRs across GBK, WordPress-iOS, WordPress-Android, and wp-calypso; merged 7 Dependabot dependency version bump PRs in GBK; monitored app store reviews`

### Something Fun

Always include a `**Something fun:**` section. Use `[PLACEHOLDER]` for the user to fill in manually.

### General

- Keep bullet items concise but descriptive — include what was fixed/done and why it matters.
- Order work completed items roughly by impact/importance.
- Days worked and time off should be confirmed with the user.

## Presenting the Draft

1. Present the full draft to the user in the conversation.
2. Ask the user to review and suggest changes (days worked, time off, missing items, corrections, etc.).
3. Iterate on feedback until the user approves.
4. Once approved, copy the final Markdown to the clipboard using `pbcopy`.
