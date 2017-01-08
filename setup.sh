#!/bin/bash

DOTFILES_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Clone tmux plugin manager
git clone https://github.com/tmux-plugins/tpm ${DOTFILES_DIR}/tmux/plugins/tpm

# Link config files
sh ${DOTFILES_DIR}/link.sh
