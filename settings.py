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

#can be both str and discord snowflake IDs.
POLL_ALLOWED_CHANNELS = ["polls"]

#emojis dict. May be possible to change incomprehensible unicode to other strings recognized by discord
EMOJIS = {
	"thumbsup": "\U0001f44d",
	"thumbsdown": "\U0001f44e",
	"shrug": "\U0001f937",
}

ADMIN_ROLE = ["Server Admin", "Bot Admin"]
GESTION_ROLES = ["Community Manager", "Server Admin"]
DEV_ROLES = ["Dev"]
for role in ADMIN_ROLE:
	GESTION_ROLES.append(role)
	DEV_ROLES.append(role)

SLAPPED_LOG_FILE = "slapped.txt"
ENABLED_EXTENSIONS_FILE = "enabled_ext.txt"


#logging settings
LOGGING_HANDLER 	= logging.FileHandler("forebot.log", "a")
LOGGING_FORMATTER	= logging.Formatter("[%(asctime)s]:%(name)s:%(message)s")
LOGGING_LEVEL		= "WARNING"
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)
LOGGING_HANDLER.setLevel(LOGGING_LEVEL)
