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

# Install Homebrew packages
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew bundle --file=${MY_DOTFILES}/Brewfile

# Install pure-prompt
yarn global add pure-prompt

# Install Atom packages
apm install --packages-file ${MY_DOTFILES}/atom/packages.txt

# Install Code packages
cat ${MY_DOTFILES}/vscode/packages.txt | xargs -n 1 code --install-extension

# Link files with rcup
env RCRC=$HOME/.dotfiles/rcrc rcup
