import logging


#########################################
#										#
#										#
#			Global Variables			#
#										#
#										#
#########################################


PREFIX = "::"
TOKEN = "your_token"
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
	"no_entry_sign": "\U0001F6AB"
}


#########################################
#										#
#										#
#				  Files					#
#										#
#										#
#########################################

#files
ENABLED_EXTENSIONS_FILE = "enabled_exts.json"
SLAPPING_FOLDER = "slapping"
CONFIG_FOLDER = "servers"
#roles
ROLES_LEVEL = ["manager", "admin"]

#default JSON files
DEFAULT_EXTENSIONS_JSON = '''{
	"Slapping": false,
	"BotEssentials":true,
	"Role":false,
	"Embedding":false,
	"Config":false,
	"Poll":false
}'''

DEFAULT_SLAPPED_FILE = '''{
	"463665420054953995": 0
}'''

DEFAULT_SERVER_FILE = '''{
    "poll_channels": [],
    "todo_channel": false,
    "roles": {
        "manager": [],
        "admin": []
    },
    "messages": {
        "welcome": false,
        "goodbye": false
    },
    "advertisement": false

}'''

#########################################
#										#
#										#
#				Logging					#
#										#
#										#
#########################################



LOG_FILE = "forebot.log"
LOGGING_HANDLER 	= logging.FileHandler(LOG_FILE, "a")
LOGGING_FORMATTER	= logging.Formatter("[%(asctime)s]:%(name)s:%(message)s")
LOGGING_LEVEL		= logging.INFO
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)

#########################################
#										#
#										#
#				 Errors					#
#										#
#										#
#########################################


ERR_NO_SUBCOMMAND = "You didn't provide any subcommand. See `::help <command>` for more info on command usage."
ERR_UNEXCPECTED = "An unexcpected error occured. Please report a bug in {} or contact an admin of your server."
ERR_NOT_ENOUGH_ARG = "This command requires additional arguments. See `::help <command>` to get more information on the command's usage"
ERR_UNSUFFICIENT_PRIVILEGE = "You don't have the permission to do this..."
ERR_NOT_SETUP = "This server hasn't been configured. If you're the owner of the server you can initialise the bot by doing `::cfg init` in any channel. You won't be able to use the bot before that."
ERR_CANT_SAVE = "Couldn't save settings to JSON configuration file."