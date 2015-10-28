# dcalhoun dotfiles
I use [thoughtbot/dotfiles](https://github.com/thoughtbot/dotfiles) as the
foundation of my personal configuration. These files are the `.local`
modifications that build on top of the foundation.

## Requirements
Set zsh as your login shell:

    chsh -s $(which zsh)

## Install
Install [rcm](https://github.com/thoughtbot/rcm):

    brew tap thoughtbot/formulae
    brew install rcm

Clone Thoughtbot's dotfiles:

    git clone git://github.com/thoughtbot/dotfiles.git
    env RCRC=$HOME/dotfiles/rcrc rcup

Then clone mine:

    git clone git://github.com/dcalhoun/dotfiles.git ~/dotfiles-local

And re-run rcup to link:

    rcup


This will create symlinks for config files in your home directory from
Thoughtbot's dotfiles and my local customizations.

You can safely run `rcup` multiple times to update:

    rcup

## Credits
Most of my configuration is small changes on top of thoughtbot's dotfiles.
They have a great series of blog posts about dotfile configuration at their
[blog](http://robots.thoughtbot.com).

This software is free and distributable under the MIT license.
