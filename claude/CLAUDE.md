# CLAUDE.md

## Rules

A list of rules that Claude _MUST_ be followed:

- NEVER use the `-C` flag for `git` commands when you are already in the targeted directory.
- ALWAYS mark pull requests as "Draft" when opening them, unless explicitly instructed otherwise.
- ALWAYS follow the Conventional Commits specification for commit messages, including pull request titles and descriptions.
- NEVER use Conventional Commit titles for issues.
- ALWAYS name branches following the Conventional Commits specification (e.g., `fix/your-branch-name`).
- ALWAYS follow a project's GitHub repository contributing guidelines if they exist.
- ALWAYS adhere to a project's GitHub pull request template if it exists.
- ALWAYS avoid combining shell commands (e.g. `&&`, `;`, custom shell script), unless absolutely necessary; run them separately.
- ALWAYS avoid running `cd` when you are already in the targeted directory. If you repeatedly need `cd`, stop to verify your current working directory.
- NEVER fill out a pull request body/template yourself. Instead, append your own "Agent summary" within a `<details/>` section at the end.
- ALWAYS keep PR descriptions concise.
- ALWAYS keep commit messages concise—the title should describe what, the body should describe why.
- ALWAYS keep code comments concise (e.g., one or two sentences). Only insert them when deemed necessary and focus on the "why" for the final state rather than including reasoning about the steps taken to get there.

## Best Practices

A list of best practices that Claude _SHOULD_ follow:

- Commit changes in small, logical chunks to make it easier for reviewers to understand the changes.
- Commit early and often to avoid reaching a state where changes are too entangled to commit separately.
- If a project's auto-formatter changes files you are editing (via agent hook or otherwise), stop to first auto-format the targeted file and commit the styling changes as a separate commit, then continue your own edits to commit separately. Do not attempt to circumvent the auto-formatter with `sed` or other tools.
- Avoid unnecessary or overly verbose comments in code, particularly if the code is self-explanatory. If a comment is needed, ensure it is clear and concise.
- Any comments should describe the end state (compared to the base branch) and why. They should not describe our journey to arriving there.
