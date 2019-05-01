#########################################
#										#
#										#
#			Global Variables			#
#										#
#										#
#########################################


PREFIX = "::"
TOKEN = "NTYzODQ4MDcxMjE0MjY4NDI5.XMjofQ.c0Chs2b0q4Wjp2yqh3MuWfhDU0M"
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
TODO_FILE = "todo.txt"
