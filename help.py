import logging
import os
import json
import discord
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

class Help(discord.ext.commands.DefaultHelpCommand):
	"""docstring for Help. An interactive object that issues help to the servers and DMs."""
	def __init__(self, language, **options):
		super(Help, self).__init__(**options)
		self.lang = language
		self.hstr = self.load_help()

	def load_help(self):
		help_dict = {}
		for ext in os.listdir(os.path.join("lang", "help")):
			if ext[-2:] == self.lang:
				with open(os.path.join("lang", "help", ext), "r") as file:
					help_dict[ext[:-3]] = json.load(file)

		return help_dict

	async def send_bot_help(self, mapping):
		print(self.command_attrs)

	async def send_cog_help(self, cog):
		print(self.cog, cog)

	async def send_group_help(self, group):
		print(group)

	async def send_command_help(self, command):
		#print(command.help, command.qualified_name)
		print(command.cog, command.parents)
		title = f"**{command.name.title()}**"

		if command.cog:
			title += f" from extension **{command.cog.qualified_name}**"

		description, usage = self.load_help()[command.cog.qualified_name.lower()][command.name]
		usage = "`" + command.name + " " + usage

		embed_help = discord.Embed(
			title = title,
			description = description,
			color = 7506394)

		embed_help.add_field(name="Usage", value=usage)
		await self.get_destination().send(embed=embed_help)
