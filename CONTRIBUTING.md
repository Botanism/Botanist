# Contributing

## Rules

Although contributing to the project is allowed and even encouraged it has to follow a few rules in order to actually benefit the project.

- First of each update feature change/addition should be made in its own PR. Having multiple new features in a single PR is discouraged.

- The PR should not enter in conflict with the branch it's compared to. This excludes PR related to changing features which will obviously change the code. The intent is to preserve the global state of the code to allow other developers to keep up to date more easily and have some sort of consistency. For example you shouldn't change the name of global settings located in `settings.py`; unless that is the point of the PR.
- Your code should follow [PEP8](https://www.python.org/dev/peps/pep-0008/) standards. The only allowed exception is the use of tabs instead of spaces. That is if your tabs are **four** spaces wide.
- All extensions should be properly configure to generate nice logs using the `logging` module. However this is easy as you only have to copy/paste the according section of code (see any extension for further information)
- All checks that you wish to include should be put in `checks.py`



This is a *guideline* which means that some exceptions may be made. However it is recommend that you respect it for your contribution to be validated. If you have any other question or think a point is unclear or too limiting feel free to contact an @admin

## Installing an editing

### Requirements

You will need python 3 and the library `discord.py`.

*(We would also recommend to work on Linux :penguin:)*

### The serious stuff

Fork the repository from the [GitHub page](https://github.com/s0lst1ce/ForeBot). This will make a copy of the repo on your account.

Then, on your computer, go to the directory where you want to install the bot and do this command:

`git clone https://github.com/s0lst1ce/ForeBot.git`

Then:

`cd ForeBot` 

And there you go! This is a fast [explanation](https://discordapp.com/developers/docs/intro#bots-and-apps) about how to "create" a bot form the official discord's doc. You have to make an "app" and then you'll have a token in the "Bot" section of your App you will be able to see/copy your token.

You'll have to copy this token to put it in the file `settings.py`. **Warning! Make sure to don't commit your token, remove it before!** If you accidentally commit it you can regenerate it.

You'll also have to invite the bot on your developing server.

To run the bot you just have to execute this command in your shell: 

`python executioner.py` (depending on your installation you'll maybe have to use the command `python3`)

You're now able to edit the Bot! :tada: :confetti_ball:

### Pull Requesting!

Now that you have improve our bot you have to publish what you did! For that you have to make a Pull Request (PR), it's like a proposition.

Please respect the [Rules](#Rules) and then your improvement will be quickly accepted! :smile:

You have to commit what you've done to your forked repository (on **your** GitHub account), and  then when it's done to push them.

After that you have to make a PR, for that you can use a client (e.g. GitKraken) or do it directly from the GitHub website. Go on the forked repo (e.g. https://github.com/YOUR_NAME/ForeBot) and then go to the "Pull Requests" tab (between Code and Projects). Now click on "New Pull Request", select `s0lst1ce/ForeBot` for the "base repository" and your repo for the "head repository". *For both ones, select the right branch.*

Then you can submit your PR, after that we will review your PR to avoid conflicts. It may takes few days, be patient, but you will certainly be in touch threw the GitHub's messages: :wink: