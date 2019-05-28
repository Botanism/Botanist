#!/usr/bin/env python3

import discord
from discord.utils import find as dfind
from settings import *
from checks import *
import math
import time
import random
import logging


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
		#appending new extension to ENABLED_EXTENSIONS_FILE
		with open(ENABLED_EXTENSIONS_FILE, "a") as file:
			file.write("{}\n".format(extension))

	except FileNotFoundError as e:
		#if the file didn't yet exist a new one will be created. This should not happen, only here as a failsafe
		main_logger.warning("{} doesn't exist.".format(ENABLED_EXTENSIONS_FILE))
		with open(ENABLED_EXTENSIONS_FILE, "w") as file:
			file.write("{}\n".format(extension))

	except Exception as e:
		#logging any other possible issue
		await ctx.send("UnexpectedError:\tReport issue to an admin")
		raise e

	await ctx.send("Successfully added and loadded {}".format(extension))
@ext.command()
async def rm(ctx, extension:str):
	try:
		bot.unload(extension)

	except Exception as e:
		main_logger.exception(e)
		await ctx.send("UnexpectedError:\tReport issue to an admin\n{}".format(e))
		raise e

	#if the extension was correctly unloaded, removing it from the enblaed extension file
	try:
		with open(ENABLED_EXTENSIONS_FILE, "aw") as file:
			lines = []
			for line in file.readlines():
				if line == extension:
					continue
				lines.append(line)
			file.write(lines)
	except Exception as e:
		main_logger.exception(e)
		await ctx.send("UnexpectedError:\tReport issue to an admin\n{}".format(e))
		raise e



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
		for ext in file.readlines():
			try:
				bot.load_extension(str(ext[:-1]))
				main_logger.info("Loaded {}".format(ext))
			
			except Exception as e:
				main_loggerre.exception(e)
				raise e

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