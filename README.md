# discord-cli
A command line interface to use Discord.

## DISCLAIMER - PLEASE READ
This is for the 99.7% who refuse to read Discord ToS (and possibly this disclaimer as well).

This project wasn't meant to replace Discord's official client in any way shape or form.    
If your account gets banned, don't create 700 Github Issues with your 2000 alts. You have been warned here.

Using this program with a user account is much more dangerous than with a bot account. I'm using `discord.py v2.x` here. The `discord.py` library sends specific `user-agent`s in its requests to the Discord API to indicate it is not a regular client, which means it's not hard for Discord to detect that you aren't using the official client.

This program allows basic interactions like sending messages and switching channels. However, be aware that using external clients has always been against Discord's terms of service.

If you've finished reading this and still want to continue with this CLI project, feel free to continue reading! Otherwise, you better close this tab and clear your history before you get bANNed!

TL;DR: Don't blame me if you get banned.

## Is this project meant for production?
No.    
This project is **far from complete** and is more of a learning tool. It's not meant to replace the official Discord client.

You can read through the code and maybe learn a few things though :)

## How do you use this?
I assume you already have at least Python 3.10 installed due to the latest updates using `discord.py v2.x`.    
I also assume you have `git clone`d this repository.

1. Install requirements from `requirements.txt`:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. Run the file:
   ```bash
   python main.py -t=<YOUR BOT/USER ACCOUNT TOKEN> -c=<CHANNEL ID>
   ```

3. Example usage:
   ```bash
   python main.py -t=MjM4NDk0NzU2NTIxMzc3Nzky.CunGFQ.wUILz7z6HoJzVeq6pyHPmVgQgV4 -c=381870553235193857
   ```

You can run the CLI without providing a token or a channel ID. If you do not provide a token, you will be prompted to include your email/password. This method does not work reliably anymore, especially if you have not logged into Discord for a long time. It is highly recommended to provide a bot token. 2FA is supported in this case. You must include a bot token if you are running this for bot accounts.

If you do not provide a channel ID, the user will log in with no specified channel. You will have to manually input a channel ID for the CLI to work.

## Example of CLI Usage:
![CLI Example](https://i.imgur.com/QvY5GIM.png)    

## Error Handling Example:
![Error Example](https://i.imgur.com/z0kPupy.png)    

## Key Updates in This Version:
- **Asynchronous Compatibility**:
  - Updated for `discord.py v2.x` to use asynchronous handling (`await`) for functions such as `add_cog` and `load_extension`.
  - Proper management of event loops in Python 3.10+, with the use of `asyncio.run()` and `asyncio.create_task()`.
  
- **Improved Session Management**:
  - Ensured proper closure of `aiohttp.ClientSession()` to prevent resource leaks.

## Planned Features:
- [ ] Commands! 
  - [x] /lenny
  - [x] /shrug
  - [x] /channel <CHANNEL ID>
  - [ ] /embed (coming soon)

- [x] Remove f-strings for compatibility with Python 3.5+.

## How can you help?
Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to contribute.

---

### **Changelog**:
- **v2.x**:
  - Refactored the code to work with `discord.py v2.x`.
  - Fixed issues with async functions (`add_cog`, `load_extension`).
  - Updated session handling and error management for the new event loop changes in Python 3.10+.
  - Added asynchronous support for commands and cogs.