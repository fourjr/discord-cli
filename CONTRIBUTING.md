# Contributing to fourjr/discord-cli

Pull requests are always cool! How'd you get started configuring your workspace and all though? Read on.

## Setting up the environment

If you already have `discord-cli` working in a location, it should be good enough to edit the code from there and test it out! However, there are a few guidelines that comes when you want to open a pull request and get it merged:

- The code must follow [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/) at all times. Docstrings for all functions/commands have to be present.
- All new features must be **locally tested**. They should be tested with *bot accounts* as that is the main type of login that we are supporting. Testing it with *user accounts* are fine too, but not completely required.
- All commands that send embeds must not send an embed if `bot.is_bot` is `False`.
- Your attitude can't be shit, if you are asked to modify something or make something better, or the community tells you better ways to do x, you can't have the "it works" attitude ¯\\\_(ツ)_/¯
- Open PRs for a use. And that use can't be to get your name in that contributors list.
- Use `cprint` and not `print` to include a spark of color!

## The PR itself

Ensure the title helps other people understand what your edit does at first glance. It doesn't have to be descriptive though. `Adds a cat command`, that's fine :)