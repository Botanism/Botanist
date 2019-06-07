import discord
import json
import logging
from settings import *
from utilities import *

class Feedback(commands.Cog):
	"""A suite of commands meant to let users give feedback about the bot: whether it's suggestions or bug reports.
	It's also meant to let server owners know when there's an update requiring their attention."""
	def __init__(self, bot):
		self.bot = bot


	@commands.command
	@commands.is_owner()
	async def update(self, message="The bot has been updated. Look at the development server for more information"): #should message be put in settings.py ?
		'''Lets the owner of the bot update the bot from github's repositery. It also sends a notification to all server owners who use the bot. The message sent in the notification is the description of the release on github.
		NB: as of now the bot only sends a generic notification & doesn't update the bot.'''
		for g in self.bot.fetch_guilds():
			#getting the dm with the server owner
			dm = g.owner.dm_channel
			if dm ==None:
				dm = g.owner.create_dm()

			#sending the server owner the updates
			dm.send(message)