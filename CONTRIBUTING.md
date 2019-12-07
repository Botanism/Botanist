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

You will need python >= 3.7 and the library [discord.py](https://github.com/Rapptz/discord.py) >=1.2.5.

### The serious stuff

Fork the repository from the [GitHub page](https://github.com/s0lst1ce/Botanist). This will make a copy of the repo on your account.

Now you need to clone the repository, you can do it using your favourite client (e.g. GitHub Desktop, GitKraken...) or you can do it using your terminal with this command:

`git clone https://github.com/s0lst1ce/Botanist.git`

Then:

`cd Botanist` 

And there you go! This is a fast [explanation](https://discordapp.com/developers/docs/intro#bots-and-apps) about how to "create" a bot form the official discord's doc. You have to make an "app" and then you'll have a token in the "Bot" section of your App you will be able to see/copy your token.

**Tokens are precious as they give full access to your bot so be careful with them!** To run the bot you first need to set the environment variable `DISCORD_TOKEN` to the value of your bot's token. Otherwise the bot won't start.

You'll also have to invite the bot on your developing server.

To run the bot you just have to execute this command in your shell: 

`python main.py` (depending on your installation you may have to use the command `python3`)

You're now able to edit the Bot! :tada: :confetti_ball:

### Pull Requesting!

Now that you have improve our bot you have to publish what you did! For that you have to make a Pull Request (PR), it's like a proposition.

Please respect the [Rules](#Rules) and then your improvement will be quickly accepted! :smile:

You have to commit what you've done to your forked repository (on **your** GitHub account), and  then when it's done to push them.

After that you have to make a PR, for that you can use a client (e.g. GitKraken, SublimeMerge) or do it directly from the GitHub website. Go on the forked repo (e.g. https://github.com/YOUR_NAME/Botanist) and then go to the "Pull Requests" tab (between Code and Projects). Now click on "New Pull Request", select `s0lst1ce/Botanist` for the "base repository" and your repo for the "head repository". *For both ones, select the right branch.*

Then you can submit your PR, after that we will review your PR to avoid conflicts. It may take few days, please be patient, we'll always seriously consider any submission :wink:

## Translating

Since `v2.0` the bot now supports translation. However these translations are not made by the maintainer of the repository ([s0lst1ce](https://github.com/s0lst1ce)) but by different individuals from the community. Hence this section explains how such people should start begin their journey. First and foremost, previous explanations apply within the applicable limit. That means that code specific notices should be ignored if you're only translating. However general [rules](#Rules) shouldn't!
As for translation itself it is recommended to use a good text editor with syntax highlighting. This is because no translation tool exists for our format (as far as we know) and that we use JSON files. A good choice would be to use [SBT3](https://www.sublimetext.com/) but any similar tool will do the trick.
Now that you're setup let's get into the real thing. You should know that all you will do, you will within the `lang` folder. As explained and developed in #73 the structure of this folder is the following: ```
lang
 - ext1
  - help.**
  - strings.**
 - ext2
  - help.**
  - strings.**```
Where `ext` is the name of the extension (eg: `slapping`) or `config`. As you can see each of this folder contains multiple files all named `help.**` and `strings.**`. Where `**` stands for the 2-letter language code (eg: `en` for english or `fr` for french). The `help.**` file contains the text that will be used by the help command to give information about the commands of the extension. This is organized like this:
```json
{
	"command_qualified_name": ["short description", "signature", "long_description"]
}
```
The second file, `strings.**` contains all the text that might be sent to the user by the bot and hence needs to be translated. These strings (=text) will be used directly in the source code files.
Now that you know this it will seem much easier to translate. What you have to translate are the keys, that means anything encapsulated in `"` and after the `:`.
Once you're done translating you should make a PR. We understand that translating the entire bot may be hard, and take time. Thus we allow you to translate only parts of it and propose this change. If we accept, we still need all strings to exist in all files. This means that if there's a string you have not yet translated you should put the english translation instead. If you do all this we will merge the changes. As we may not know the language you've translated to please do your best to keep the same level of language and don't start altering the meaning of the original (english) strings.
I hope this will get you started! Come and try, we're nice ;)