# CLAUDE.md

## Rules

A list of rules that Claude _MUST_ be followed:

- Avoid using the `-C` flag for `git` commands when you are already in the targeted directory.
- When opening GitHub pull requests, always mark them as "Draft" unless explicitly instructed otherwise (i.e., use the `gh` CLI `--draft` flag).
- Follow the Conventional Commits specification for commit messages, including pull request titles and descriptions. DO NOT use Conventional Commit titles for issues.
- Name branches following the Conventional Commits specification (e.g., `fix/your-branch-name`).
- Follow a project's GitHub repository contributing guidelines if they exist.
- Adhere to a project's GitHub pull request template if it exists.
- Unless absolutely necessary, always avoid combining commands with `&&` or `;` as it requires custom bash script permission. Run them separately (e.g., `git add` then `git commit`).
- Avoid running `cd` when you are already in the targeted directory. If you repeatedly need `cd`, stop to verify your current working directory.

## Best Practices

A list of best practices that Claude _SHOULD_ follow:

- Commit changes in small, logical chunks to make it easier for reviewers to understand the changes.
- If a project's auto-formatter changes files you are editing (via agent hook or otherwise), stop to first auto-format the targeted file and commit the styling changes as a separate commit, then continue your own edits to commit separately. Do not attempt to circumvent the auto-formatter with `sed` or other tools.
