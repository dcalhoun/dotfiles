# CLAUDE.md

## Rules

A list of rules that Claude _MUST_ be followed:

- Avoid using the `-C` flag for `git` commands when you are already in the targeted directory.
- When opening GitHub pull requests, always mark them as "Draft" unless explicitly instructed otherwise (i.e., use the `gh` CLI `--draft` flag).
- Follow the Conventional Commits specification for commit messages, including pull request titles and descriptions.
- Name branches following the Conventional Commits specification (e.g., `fix/your-branch-name`).
- Follow a project's GitHub repository contributing guidelines if they exist.
- Adhere to a project's GitHub pull request template if it exists.

## Best Practices

A list of best practices that Claude _SHOULD_ follow:

- Commit changes in small, logical chunks to make it easier for reviewers to understand the changes.
