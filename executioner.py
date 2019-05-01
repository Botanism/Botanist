#!/usr/bin/env python3

import discord
from discord.utils import find as dfind
from settings import *
from checks import *
import math
import requests as rq
from bs4 import BeautifulSoup
import time
import random



#INITS THE BOT
bot = commands.Bot(command_prefix=PREFIX)


#########################################
#										#
#										#
#			Setup & Execution			#
#										#
#										#
#########################################


#command that lets admin update the bot without shutting it down
@bot.command()
@commands.has_any_role(*ADMIN_ROLE)
async def reload(ctx, extension:str):
	try:
		bot.reload_extension(extension)
	except Exception as e:
		raise ctx.send("Couldn't reload extension {} because:```python\n{}```".format(extension, e))




bot.load_extension("BotEssentials")
bot.load_extension("Role")
bot.load_extension("Slapping")
bot.load_extension("Embedding")
bot.load_extension("Poll")

bot.run(TOKEN)