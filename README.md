# discord-cli
A command line interface to use Discord.

## DISCLAIMER - PLEASE READ
This is for the 99.7% who refuse to read Discord ToS (and possibly this disclaimer as well).

This project wasn't meant to replace discord's official client in any way shape or form.    
If your account gets banned, don't come creating 700 Github Issues with you 2000 alts. I already warned you here.

Using this program with a user account is much more dangerous than a bot account. I'm using `discord.py 1.0.0a` right here. It has `user-agent`s in it's requests to the Discord API to say that it isn't a client which means it isn't hard for Discord to realise that you aren't using the client.

This program will also allow you to send embeds (in the future). Sending these will raise a high alert as user accounts technically in the official clients aren't allowed to do this.

Using external clients were against Discord's wish and will from the start. Always was against the terms of service but there are still people who do this. 

If you have finished reading this, and still want to have some super cool command line discord, go ahead and read on! Else, you better close this tab and clear your history before you get bANNed!

TL;DR Don't blame me if you get banned.

## Is this project meant for production?
No.    
This project is **far from complete**. Refer to some of the below sections for further explanation.

You can read through the code and maybe learn some new things though :)

## How do you use this?
I assume you already have at least Python 3.5 installed.    
I also assume you have `git clone`d this.

Install requirements from `requirements.txt`
```
python -m pip install -r requirements.txt
```

Run the file
```
python main.py -t=<YOUR BOT/USER ACCOUNT TOKEN> -c=<CHANNEL ID>
```

An example
```
python main.py -t=MjM4NDk0NzU2NTIxMzc3Nzky.CunGFQ.wUILz7z6HoJzVeq6pyHPmVgQgV4 -c=381870553235193857
```

You can run the CLI without providing a token or a channel ID. If you do not provide a token, you will be prompted to include your email/password. This method does not work all the time, especially if you have not logged into Discord for a long time. It is still highly recommended to provide a token. 2FA is supported in this case. Of course, you would have to include a token if you are going to run this on the bot account.

If you do not provide a chnanel ID, the user will log in with no specified channel. You would have to then input a channel ID for the CLI to work.

![image](https://i.imgur.com/QvY5GIM.png)    
*An example of a functioning CLI*

![image](https://i.imgur.com/z0kPupy.png)    
*The CLI Error Handling*

## What else do I want to be here?
- [ ] Commands! 
  - [x] /lenny
  - [x] /shrug
  - [x] /channel <CHANNEL ID>
  - [ ] /embed

- [x] Remove f-strings - py3.5 compaitibility

## How can you help?
[CONTRIBUTING.md](CONTRIBUTING.md)
