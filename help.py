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
		print(self.paginator)
		try:
			self.paginator.add_line(line="My test line")
			for page in self.paginator.pages:
				await self.get_destination().send(page)
			full_help = {}
			for cog in mapping:
				if isinstance(cog, discord.ext.commands.Cog):
					full_help[cog.qualified_name] = {}
					for cmd_grp in mapping[cog]:
						#maybe change this in the future to define complete help, sub-groups & subcommands alike
						if isinstance(self.hstr[cog.qualified_name.lower()][cmd_grp.qualified_name], list):
							full_help[cog.qualified_name][cmd_grp.qualified_name] = self.hstr[cog.qualified_name.lower()][cmd_grp.qualified_name][0]
						else:
							full_help[cog.qualified_name][cmd_grp.qualified_name] = self.hstr[cog.qualified_name.lower()][cmd_grp.qualified_name]

				else:
					await self.context.send(embed=get_embed_err(ERR_UNEXCPECTED))

			print("Full help:\n", full_help)
			pages = []
			for cog in full_help:
				page = self.make_page(dict(cog, full_help[cog]), lvl=0)
				pages.append(page)

			explanation = "This is the homepage of the `help` command. You can navigate through it using the reactions. Or you can query more specific commands/cogs/groups."
			embed = discord.Embed(title = "Help's help ;)",
				description = explanation,
				color = 7506394)

			await self.get_destination().send(embed=embed)

		except:
			raise

	def make_page(self, commands, lvl=None):
		assert lvl!=None, TypeError("lvl needs to be defined")
		page = ""
		page.join("**")

