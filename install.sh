#!/bin/sh

# Globals
MY_DOTFILES=$HOME/.dotfiles
TB_DOTFILES=$HOME/.dotfiles-thoughtbot

# Update default shell
if [ $(basename $SHELL) = "zsh" ]; then
  echo "✅ Default shell is zsh."
else
  echo "🛠 Setting default shell to zsh..."
  chsh -s $(which zsh)
fi

# Install thoughtbot/dotfiles
if [ -e $TB_DOTFILES ]; then
  echo "✅ thoughtbot dotfiles installed."
else
  echo "🛠 Cloning Thoughtbot dotfiles..."
  git clone https://github.com/thoughtbot/dotfiles.git $TB_DOTFILES
fi

# Install tpm
if [ -e ${MY_DOTFILES}/tmux/plugins/tpm ]; then
  echo "✅ tpm installed."
else
  echo "🛠 Installing tpm..."
  git clone https://github.com/tmux-plugins/tpm ${MY_DOTFILES}/tmux/plugins/tpm
fi

# Install Homebrew
if which brew > /dev/null; then
  echo "✅ Homebrew installed."
else
  echo "🛠 Installing Homebrew..."
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
fi

# Install Homebrew packages
echo "🛠 Installing Homebrew packages..."
brew bundle --file=${MY_DOTFILES}/Brewfile

# Install Node.js
if which node > /dev/null; then
  echo "✅ Node.js installed."
else
  echo "🛠 Installing Node.js..."
  asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
  asdf install nodejs latest
  asdf global nodejs latest
  asdf shell nodejs latest
fi

# Link files with rcup
echo "🔗 Linking dotfiles"
env RCRC=$HOME/.dotfiles/rcrc rcup

# Disable macOS character accent press-and-hold for VSCode and Hyper
defaults write -g ApplePressAndHoldEnabled -bool false
