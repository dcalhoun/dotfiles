chsh -s $(which zsh)

MY_DOTFILES=$HOME/.dotfiles
TB_DOTFILES=$HOME/.dotfiles-thoughtbot

if [ ! -e $TB_DOTFILES ]; then
  git clone https://github.com/thoughtbot/dotfiles.git $TB_DOTFILES
fi

if [ ! -e ${MY_DOTFILES}/tmux/plugins/tpm ]; then
  git clone https://github.com/tmux-plugins/tpm ${MY_DOTFILES}/tmux/plugins/tpm
fi

brew bundle

yarn global add pure-prompt

rcup -d $TB_DOTFILES -x README.md -x Brewfile -x LICENSE -x rcrc
rcup -f -d $MY_DOTFILES -x README.md -x Brewfile -x LICENSE -x install.sh
