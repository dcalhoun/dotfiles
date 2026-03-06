# CLAUDE.md

## Rules

A list of rules that Claude _MUST_ be followed:

- Avoid using the `-C` flag for `git` commands when you are already in the targeted directory.
- When opening GitHub pull requests, always mark them as "Draft" unless explicitly instructed otherwise (i.e., use the `gh` CLI `--draft` flag).
- Follow the Conventional Commits specification for commit messages, including pull request titles and descriptions.
- Name branches following the Conventional Commits specification (e.g., `fix/your-branch-name`).
- Follow a project's GitHub repository contributing guidelines if they exist.
- Adhere to a project's GitHub pull request template if it exists.
- Avoid combining `git` commands with `&&` as it requires custom bash script permission. Run them separately (e.g., `git add` then `git commit`).
- When requested to create a new branch for work, also create a new Git worktree using the `ga` function defined in `zsh/functions/ga` (e.g., `ga feat/my-branch`). This creates the worktree, checks out the branch, and changes into the worktree directory.

## Best Practices

A list of best practices that Claude _SHOULD_ follow:

- Commit changes in small, logical chunks to make it easier for reviewers to understand the changes.
