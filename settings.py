import logging
#########################################
#										#
#										#
#			Global Variables			#
#										#
#										#
#########################################


PREFIX = "::"
TOKEN = "NTYzODQ4MDcxMjE0MjY4NDI5.XOUOKA.WQ4i2B_Jer-mWptaXZlrsNsMVF0"
RUNNER_ID=289426079544901633

#server with all of the bot's devs. Where all bug reports should be made.
DEV_SRV = 564213369834307600

#emojis dict. May be possible to change incomprehensible unicode to other strings recognized by discord
EMOJIS = {
	"thumbsup": "\U0001f44d",
	"thumbsdown": "\U0001f44e",
	"shrug": "\U0001f937",
	"wastebasket": "\U0001F5D1",
	"check": "\U00002705",
	"hourglass": "\U000023F3",
	"wave": "\U0001F44B"
}

ROLES_FILE = "roles.txt"
SLAPPED_LOG_FILE = "slapped.txt"
ENABLED_EXTENSIONS_FILE = "enabled_ext.txt"
POLL_ALLOWED_CHANNELS_FILE = "poll_channels.txt"
TODO_CHANNEL_FILE = "todo_channel.txt"
TODO_TYPES_FILE = "todo_types.txt"
WELCOME_MESSAGE_FILE = "welcome_messages.txt"

#data used only for Todo -> maybe remove it ?
PUBLIC_REPOST="Public repost"

#logging settings
LOGGING_HANDLER 	= logging.FileHandler("forebot.log", "a")
LOGGING_FORMATTER	= logging.Formatter("[%(asctime)s]:%(name)s:%(message)s")
LOGGING_LEVEL		= logging.WARNING
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)

#generic error messages
ERR_NO_SUBCOMMAND = "You didn't provide any subcommand. See `::help <command>` for more info on command usage."
ERR_UNEXCPECTED = "An unexcpected error occured. Please report a bug in {} or contact an admin of your server.".format(DEV_SRV)
ERR_NOT_ENOUGH_ARG = "This command requires additional arguments. See `::help <command>` to get more information on the command's usage"
ERR_UNSUFFICIENT_PRIVILEGE = "You don't have the permission to do this..."



'''#DEPRECATED
CHANNELS = {
	"rules": 566569408416186377,
	"faq": 566618400307019776
}


#DEPRECATED
ADMIN_ROLE = ["Server Admin", "Bot Admin"]
GESTION_ROLES = ["Community Manager", "Server Admin"]
for role in ADMIN_ROLE:
	GESTION_ROLES.append(role)
'''