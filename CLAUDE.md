# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal dotfiles repository that extends [thoughtbot/dotfiles](https://github.com/thoughtbot/dotfiles). Files here are `.local` overrides that layer on top of the thoughtbot foundation. The repository uses [rcm](https://github.com/thoughtbot/rcm) to symlink dotfiles to the home directory.

## Installation and Setup

```bash
# Full installation (clones thoughtbot/dotfiles, installs Homebrew packages, links files)
./install.sh

# Re-link dotfiles after changes
env RCRC=$HOME/.dotfiles/rcrc rcup -q

# Install Homebrew packages
brew bundle --file=Brewfile
```

## Key Architecture

**Dotfile Layering**: This repo (`~/.dotfiles`) + thoughtbot dotfiles (`~/.dotfiles-thoughtbot`) are both specified in `rcrc`. Local files override thoughtbot defaults via the `.local` suffix convention (e.g., `zshrc.local` extends thoughtbot's `zshrc`).

**Config Locations**:
- `config/ghostty/` - Ghostty terminal configuration
- `claude/skills/` - Claude Code custom skills (submodules)
- `tmux/plugins/` - tmux plugins managed by tpm
- `vim/custom-snippets/` - UltiSnips snippets
- `zsh/functions/` and `zsh/completion/` - Custom zsh functions and completions

## tmux

Prefix key is `C-o` (not the default `C-b`). Uses tpm for plugin management.

## Git Aliases (from gitconfig.local)

- `ba` - branches sorted by recent commits
- `fe` - fetch with prune
- `sw` - switch branch
- `tr` - set upstream tracking branch
