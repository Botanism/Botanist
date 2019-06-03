#!/usr/bin/env python3

import discord
from discord.utils import find as dfind
from settings import *
from utilities import *
import math
import time
import random
import logging
import json


#INITS THE BOT
bot = commands.Bot(command_prefix=PREFIX)

#########################################
#										#
#										#
#			Setting up logging			#
#										#
#										#
#########################################

#Creating main logger
main_logger = logging.getLogger(__name__)
main_logger.setLevel(LOGGING_LEVEL)
main_logger.addHandler(LOGGING_HANDLER)
main_logger.info(f"Initalized {__name__} logger")


#Creating discord.py's logger
discord_logger = logging.getLogger("discord")
discord_logger.setLevel(LOGGING_LEVEL)
discord_logger.addHandler(LOGGING_HANDLER)
discord_logger.info("Initalized discord's logger")


#########################################
#										#
#										#
#			Extension Manipulation		#
#										#
#										#
#########################################


#commands that lets admin update the bot without shutting it down
@bot.group()
@is_runner()
async def ext(ctx):
	if ctx.invoked_subcommand is None:
		await ctx.send(ERR_NOT_ENOUGH_ARG)

@ext.command()
async def reload(ctx, extension:str):
	try:
		bot.reload_extension(extension)
		await ctx.send("Successfully reloaded {}".format(extension))
	except Exception as e:
		await ctx.send("Couldn't reload extension {} because:```python\n{}```".format(extension, e))
		raise e

@ext.command()
async def add(ctx, extension:str):

	#trying to load the extension. Should only fail if the extension is not installed
	try:
		bot.load_extension(extension)

	except Exception as e:
		main_logger.exception(e)
		await ctx.send("UnexpectedError:\tReport issue to an admin\n{}".format(e))
		raise e

	#if the extension was correctly loaded, adding it to the enabled file
	try:
		with open(ENABLED_EXTENSIONS_FILE, "r") as file:
			enabled_exts = json.load(file)
		
		enabled_exts[extension] = True

		with open(ENABLED_EXTENSIONS_FILE, "w") as file:
			json.dump(enabled_exts, file)

	except FileNotFoundError as e:
		#if the file didn't yet exist a new one will be created. This should not happen, only here as a failsafe
		main_logger.warning("{} doesn't exist.".format(ENABLED_EXTENSIONS_FILE))
		with open(ENABLED_EXTENSIONS_FILE, "w") as file:
			file.write(DEFAULT_EXTENSIONS_JSON)

	except Exception as e:
		#logging any other possible issue
		await ctx.send("UnexpectedError:\tReport issue to an admin")
		raise e

	await ctx.send("Successfully added and loadded {}".format(extension))


@ext.command()
async def rm(ctx, extension:str):
	try:
		bot.unload_extension(extension)

	except Exception as e:
		main_logger.exception(e)
		await ctx.send("UnexpectedError:\tReport issue to an admin\n{}".format(e))
		raise e

	#if the extension was correctly unloaded, removing it from the enblaed extension file
	try:
		with open(ENABLED_EXTENSIONS_FILE, "r") as file:
			enabled_exts = json.load(file)
		
		enabled_exts[extension] = False

		with open(ENABLED_EXTENSIONS_FILE, "w") as file:
			json.dump(enabled_exts, file)

	except Exception as e:
		main_logger.exception(e)
		await ctx.send("UnexpectedError:\tReport issue to an admin\n{}".format(e))
		raise e

	await ctx.send("Successfully removed and unloaded {}".format(extension))
	local_logger.info(f"Disabled and removed {extension}")



#########################################
#										#
#										#
#			Setup & Execution			#
#										#
#										#
#########################################
#loading enabled extensions and starting
#bot

#trying to load all enabled extensions
try:
	with open(ENABLED_EXTENSIONS_FILE, "r") as file:
		extensions = json.load(file)
	for ext in extensions:
		if extensions[ext]==True:
			bot.load_extension(ext)

#if no extension is enabled
except FileNotFoundError as e:
	main_logger.warning("No extension enabled, none loaded. You probably want to configure the bot or add some extensions")
	raise e

#unexpected error handling
except Exception as e:
	main_logger.exception(e)
	raise e

#running the bot, no matter what
finally:
	bot.run(TOKEN)