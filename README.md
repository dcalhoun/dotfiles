# dcalhoun dotfiles
I use [thoughtbot/dotfiles](https://github.com/thoughtbot/dotfiles) as the
foundation of my personal configuration. These files are the `.local`
modifications that build on top of the foundation.

## Requirements
Set zsh as your login shell:

```bash
chsh -s $(which zsh)
```

## Install
Install [rcm](https://github.com/thoughtbot/rcm):

```bash
brew tap thoughtbot/formulae
brew install rcm
```

Clone and link Thoughtbot's dotfiles:

```bash
git clone git://github.com/thoughtbot/dotfiles.git ~/dotfiles
env RCRC=$HOME/dotfiles/rcrc rcup
```

Clone and link my dotfiles:

```bash
git clone git://github.com/dcalhoun/dotfiles.git ~/dotfiles-local
rcup
```

This will create symlinks for config files in your home directory from
Thoughtbot's dotfiles and my local customizations.

You can safely run `rcup` multiple times to update:

```bash
rcup
```

Setup atom config:

```bash
cd ~/dotfiles-local/atom/
./link.sh
```

## Credits
Most of my configuration is small changes on top of thoughtbot's dotfiles.
They have a great series of blog posts about dotfile configuration at their
[blog](http://robots.thoughtbot.com).

This software is free and distributable under the MIT license.
