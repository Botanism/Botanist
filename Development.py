import discord
import json
import logging
from settings import *
from utilities import *

#########################################
#										#
#										#
#			Setting up logging			#
#										#
#										#
#########################################
local_logger = logging.getLogger(__name__)
local_logger.setLevel(LOGGING_LEVEL)
local_logger.addHandler(LOGGING_HANDLER)
local_logger.info("Innitalized {} logger".format(__name__))



#########################################
#										#
#										#
#			Making commands				#
#										#
#										#
#########################################


class Development(commands.Cog):
	"""A suite of commands meant to let users give feedback about the bot: whether it's suggestions or bug reports.
	It's also meant to let server owners know when there's an update requiring their attention."""
	def __init__(self, bot):
		self.bot = bot


	@commands.command
	@commands.is_owner()
	async def update(self, ctx, message="The bot has been updated. Look at the development server for more information"): #should message be put in settings.py ?
		'''Lets the owner of the bot update the bot from github's repositery. It also sends a notification to all server owners who use the bot. The message sent in the notification is the description of the release on github.
		NB: as of now the bot only sends a generic notification & doesn't update the bot.'''
		for g in self.bot.fetch_guilds():
			#getting the dm with the server owner
			dm = g.owner.dm_channel
			if dm ==None:
				dm = g.owner.create_dm()

			#sending the server owner the updates
			dm.send(message)

	@commands.command()
	@commands.is_owner() #-> this needs to be changed to is_dev()
	async def log(self, ctx):
		'''returns the bot's log as an attachement'''
		#getting the log
		with open(LOG_FILE, "r") as file:
			log = discord.File(file)

		#sending the log
		await ctx.send(file=log)


def setup(bot):
	bot.add_cog(Development(bot))