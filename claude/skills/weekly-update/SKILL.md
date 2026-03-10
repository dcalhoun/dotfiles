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
- Search for PRs merged during the date range that reference the user's Linear issues (e.g., CMM-\* issues) — these may be authored by teammates but shepherded by the user.
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

**Something fun:**

[PLACEHOLDER]
```

### References

- Prefer Linear issue IDs/URLs as references (e.g., `[CMM-1234](https://linear.app/a8c/issue/CMM-1234)`).
- Only use GitHub PR IDs/URLs or Slack thread URLs when no corresponding Linear issue exists (e.g., `[GBK #123](https://github.com/wordpress-mobile/GutenbergKit/pull/123)`).
- Never include both a Linear ID and a GitHub PR for the same item.

### Naming

- First mention of GutenbergKit should define the acronym: "GutenbergKit (GBK)".
- All subsequent references should use "GBK".

### Misc Line

Consolidate the following into a single bullet prefixed with "Misc:" as the **last** work completed bullet:

- PR reviews (mention which repos)
- Dependabot dependency version bump PRs merged (include count)
- App store review monitoring
- Other minor/routine work

Example: `Misc: reviewed teammate PRs across GBK, WordPress-iOS, WordPress-Android, and wp-calypso; merged 7 Dependabot dependency version bump PRs in GBK; monitored app store reviews`

### Bullet Writing Style

- **Be concise.** Each bullet should be a single sentence fragment — describe _what_ was done and _why it matters_, not _how it was done_.
- **Do not elaborate** with dashes, parenthetical asides explaining impact, or multi-clause sentences. Avoid phrases like "coordinated testing", "shepherded a release", "enabling X" unless essential to understanding the item.
- Good: `Fixed Android magic login redirect infinite loop for password-less accounts`
- Bad: `Fixed an Android deep link infinite loop that trapped Jetpack users in a passwordless login cycle — coordinated testing, opened the client-side fix, and shepherded a 26.6.1 hotfix release`
- Good: `Fixed missing text alignment and typography options for sites without editor settings`
- Bad: `Added default typography settings (text alignment, font sizes, drop cap, etc.) for sites without the Gutenberg plugin REST API endpoint`
- **Include PRs authored by others that the user shepherded or merged** if they relate to the user's Linear issues. Cross-reference merged PRs (including those from teammates) against the user's Linear issues.
- **Time off should be concise** — e.g., "AFK Monday–Tuesday (3/16–3/17)" not a multi-line description of travel plans.

### Bullet Ordering

Order work completed bullets as follows:

1. **Urgent/high-impact bug fixes** first (e.g., login loops, editor failing to load)
2. **Feature work and other bug fixes** next
3. **Test infrastructure and CI improvements** next
4. **Dependency/build tooling fixes** next
5. **In-progress work** (items where a PR was opened but not yet merged) last, just before Misc
6. **Misc** always last

### Commitments This Week

- Keep to 2–3 items maximum.
- Use concise action-oriented language.
- Combine related items into a single bullet when possible (e.g., multiple Linear issues for the same feature).

### Something Fun

Always include a `**Something fun:**` section. Use `[PLACEHOLDER]` for the user to fill in manually.

### General

- Days worked and time off should be confirmed with the user.

## Presenting the Draft

1. Present the full draft to the user in the conversation.
2. Ask the user to review and suggest changes (days worked, time off, missing items, corrections, etc.).
3. Iterate on feedback until the user approves.
4. Once approved, copy the final Markdown to the clipboard using `pbcopy`.
