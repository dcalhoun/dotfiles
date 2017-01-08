#!/bin/bash

DOTFILES_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ATOM_DIR=$HOME/.atom
HYPER_DIR=$HOME
TMUX_DIR=$HOME/.tmux
TMUXINATOR_DIR=$HOME/.tmuxinator

# Symlink Atom config
ln -sf ${DOTFILES_DIR}/atom/config.cson ${ATOM_DIR}
ln -sf ${DOTFILES_DIR}/atom/init.coffee ${ATOM_DIR}
ln -sf ${DOTFILES_DIR}/atom/keymap.cson ${ATOM_DIR}
ln -sf ${DOTFILES_DIR}/atom/snippets.cson ${ATOM_DIR}
ln -sf ${DOTFILES_DIR}/atom/styles.less ${ATOM_DIR}

# Symlink Hyper.app config
ln -sf ${DOTFILES_DIR}/hyper.js ${HYPER_DIR}

# Symlink tmux plugins
ln -sf ${DOTFILES_DIR}/tmux ${HOME}/.tmux

# Symlink tmuxinator templates
mkdir ${TMUXINATOR_DIR}
ln -sf ${DOTFILES_DIR}/tmuxinator/champlet.yml ${TMUXINATOR_DIR}
ln -sf ${DOTFILES_DIR}/tmuxinator/gn.yml ${TMUXINATOR_DIR}
ln -sf ${DOTFILES_DIR}/tmuxinator/gn-web.yml ${TMUXINATOR_DIR}
