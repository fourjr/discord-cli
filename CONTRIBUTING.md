# Contributing to fourjr/discord-cli

Pull requests are welcome. Please keep new Discord functionality on the
official bot/OAuth APIs; this project does not support user-account tokens or
self-bots.

## Guidelines

- Follow PEP 8 and include docstrings for new functions and commands.
- Locally test new behavior without requiring a live Discord account where
  practical; never commit a token or other credential.
- Keep Discord permissions narrow and bound message/history operations.
- MCP tools that write to Discord must be opt-in and require the MCP host to
  confirm each action. Keep the default bridge read-only.
- Use `cprint` for colored CLI output rather than `print`.

Run the offline suite with `python -m unittest discover -s tests`.
