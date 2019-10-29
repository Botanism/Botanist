import logging
import os

#########################################
#                                       #
#                                       #
#           Global Variables            #
#                                       #
#                                       #
#########################################


PREFIX = "::"
TOKEN = os.getenv("DISCORD_TOKEN", default=None)
RUNNER_ID=289426079544901633

#server with all of the bot's devs. Where all bug reports should be made.
DEV_SRV = 564213369834307600

#github website URL
WEBSITE = "https://github.com/organic-bots/ForeBot"

#invite to dev server URL
DEV_SRV_URL = "https://discord.gg/mpGM5cg"

#update message
DEFAULT_UPDATE_MESSAGE = "The bot has been updated. Look at the development server for more information"

#emojis dict. May be possible to change incomprehensible unicode to other strings recognized by discord
EMOJIS = {
    "thumbsup": "\U0001f44d",
    "thumbsdown": "\U0001f44e",
    "shrug": "\U0001f937",
    "wastebasket": "\U0001F5D1",
    "check": "\U00002705",
    "hourglass": "\U000023F3",
    "wave": "\U0001F44B",
    "no_entry_sign": "\U0001F6AB",
    "red_circle": "\U0001F534",
    "white_circle": "\U000026AA",
    "large_blue_circle": "\U0001F535",
    "tada": "\U0001F389",
    "hammer": "\U0001F528",
    "x": "\U0000274C",
    "warning": "\U000026a0",
}


#########################################
#                                       #
#                                       #
#                 Files                 #
#                                       #
#                                       #
#########################################

#Files
EXT_FOLDER = "exts"
EXTENSIONS_FILE = "enabled_exts.json"
SLAPPING_FOLDER = "slapping"
CONFIG_FOLDER = "servers"
TODO_FOLDER = "todo"

#roles
ROLES_LEVEL = ["manager", "admin"]

#default JSON files
DEFAULT_EXTENSIONS_JSON = {
    "Slapping": False,
    "BotEssentials":True,
    "Role":False,
    "Embedding":False,
    "Config":False,
    "Poll":False
}

DEFAULT_SLAPPED_FILE = {
    "463665420054953995": 0
}

DEFAULT_SERVER_FILE = {
    "poll_channels": [],
    "todo_channel": False,
    "roles": {
        "manager": [],
        "admin": []
    },
    "messages": {
        "welcome": False,
        "goodbye": False
    },
    "advertisement": False

}

DEFAULT_TODO_FILE = {
    "groups": {
    "default": []
    },
    "types": {
    "default": "000000"
    }
}

#########################################
#                                       #
#                                       #
#               Logging                 #
#                                       #
#                                       #
#########################################

LOG_FILE = "forebot.log"
LOGGING_HANDLER     = logging.FileHandler(LOG_FILE, "a")
LOGGING_FORMATTER   = logging.Formatter("\n[%(asctime)s][%(name)s]:%(message)s")
LOGGING_LEVEL       = logging.INFO
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)

#########################################
#                                       #
#                                       #
#                Errors                 #
#                                       #
#                                       #
#########################################


ERR_NO_SUBCOMMAND = ("No subcommand", "You didn't provide any subcommand. See `::help <command>` for more info on command usage.")
ERR_UNEXCPECTED = ("Unexcpected error", "An unexcpected error occured. Please report a bug in {} or contact an admin of your server.")
ERR_NOT_ENOUGH_ARG = ("Not enough arguments", "This command requires additional arguments. See `::help <command>` to get more information on the command's usage")
ERR_UNSUFFICIENT_PRIVILEGE = ("Unsufficient privileges", "You don't have the permissions to do this...")
ERR_NOT_SETUP = ("Server not setup", "This server hasn't been configured. If you're the owner of the server you can initialize the bot by doing `::cfg init` in any channel. You won't be able to use the bot before that.")
ERR_CANT_SAVE = ("Couldn't save configuration", "Couldn't save settings to JSON configuration file.")