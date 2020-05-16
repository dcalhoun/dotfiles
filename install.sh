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
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew bundle --file=${MY_DOTFILES}/Brewfile

# Install pure-prompt
yarn global add pure-prompt

# Install Atom packages
apm install --packages-file ${MY_DOTFILES}/atom/packages.txt

# Install Code packages
cat ${MY_DOTFILES}/vscode/packages.txt | xargs -n 1 code --install-extension

# Link files with rcup
rcup -d $TB_DOTFILES -x README.md -x LICENSE -x Brewfile -x install.sh -x rcrc
rcup -f -d $MY_DOTFILES -x README.md -x LICENSE -x Brewfile -x install.sh -x rcrc
