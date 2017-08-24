#!/bin/sh

# Update default shell
chsh -s $(which zsh)

# Globals
MY_DOTFILES=$HOME/.dotfiles
TB_DOTFILES=$HOME/.dotfiles-thoughtbot

# Install thoughtbot/dotfiles
if [ ! -e $TB_DOTFILES ]; then
  git clone https://github.com/thoughtbot/dotfiles.git $TB_DOTFILES
fi

# Install tpm
if [ ! -e ${MY_DOTFILES}/tmux/plugins/tpm ]; then
  git clone https://github.com/tmux-plugins/tpm ${MY_DOTFILES}/tmux/plugins/tpm
fi

# Install Homebrew package
brew bundle --file=${MY_DOTFILES}/Brewfile

# Install pure-prompt
yarn global add pure-prompt

# Install Atom packages
apm install --packages-file ${MY_DOTFILES}/atom/packages.txt

# Link files with rcup
rcup -d $TB_DOTFILES
rcup -f -d $MY_DOTFILES
