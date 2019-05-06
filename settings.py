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
AUTHOR_ID=289426079544901633


#emojis dict. May be possible to change incomprehensible unicode to other strings recognized by discord
EMOJIS = {
	"thumbsup": "\U0001f44d",
	"thumbsdown": "\U0001f44e",
	"shrug": "\U0001f937",
	"wastebasket": "\U0001F5D1",
    "check": "\U00002705",
    "hourglass": "\U000023F3"
}

#a set of channel names bound to their ids
CHANNELS = {
	"rules": 566569408416186377,
	"faq": 566618400307019776
}




ADMIN_ROLE = ["Server Admin", "Bot Admin"]
GESTION_ROLES = ["Community Manager", "Server Admin"]
DEV_ROLES = ["Dev"]
for role in ADMIN_ROLE:
	GESTION_ROLES.append(role)
	DEV_ROLES.append(role)

PUBLIC_REPOST="Public repost"

SLAPPED_LOG_FILE = "slapped.txt"
ENABLED_EXTENSIONS_FILE = "enabled_ext.txt"
<<<<<<< HEAD
POLL_ALLOWED_CHANNELS_FILE = "poll_channels.txt"
=======
>>>>>>> 69c41b626b42274ca81d5674ff0aaf6714fe15ba
TODO_CHANNEL_FILE = "todo_channel.txt"
TODO_TYPES_FILE = "todo_types.txt"

#data used only for Todo -> maybe remove it ?
 PUBLIC_REPOST="Public repost" 

#logging settings
LOGGING_HANDLER 	= logging.FileHandler("forebot.log", "a")
LOGGING_FORMATTER	= logging.Formatter("[%(asctime)s]:%(name)s:%(message)s")
LOGGING_LEVEL		= logging.WARNING
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)
