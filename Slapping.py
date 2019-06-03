import logging
import discord
import os
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


class Slapping(commands.Cog):
	"""a suite of commands meant to help moderators handle the server"""
	def __init__(self, bot):
		self.bot = bot
		if SLAPPING_FILE not in os.listdir():
			with open(SLAPPING_FILE, "w") as file:
				file.write("")

		
	@commands.command()
	@is_init()
	@has_auth("manager")
	async def slap(self, ctx, member:discord.Member):
		'''Meant to give a warning to misbehavioring members. Cumulated slaps will result in warnings, role removal and eventually kick. Beware the slaps are loged throughout history and are cross-server'''
		with open(SLAPPING_FILE, "r") as file:
			slaps = json.load(file)

		#checking wether the user has already been slapped
		if str(member.id) not in slaps[str(ctx.guild.id)]:
			slaps[str(ctx.guild.id)][str(member.id)] = 1

		else:
			slaps[str(ctx.guild.id)][str(member.id)] +=1


		#writting to file
		with open(SLAPPING_FILE, "w") as file:
			json.dump(slaps, file)

		await ctx.send("{} you've been slapped by {} because of your behavior! This is the {} time. Be careful, if you get slapped too much there *will* be consequences !".format(member.mention, ctx.message.author.mention, slaps[str(ctx.guild.id)][str(member.id)]))		

	@commands.command()
	@is_init()
	@has_auth("manager")
	async def pardon(self, ctx, member:discord.Member, nbr=0):
		'''Pardonning a member resets his slaps count.'''
		with open(SLAPPING_FILE, "r") as file:
			slaps = json.load(file)

		#checking wether the user has already been slapped
		if str(member.id) not in slaps[str(ctx.guild.id)]:
			pass

		else:
			if nbr==0 or slaps[str(ctx.guild.id)][str(member.id)]<nbr:
				slaps[str(ctx.guild.id)][str(member.id)]=0

			else:
				slaps[str(ctx.guild.id)][str(member.id)] -=nbr


		#writting to file
		with open(SLAPPING_FILE, "w") as file:
			json.dump(slaps, file)

		local_logger.info("Pardonned {0.name}[{0.id}]".format(member))
		await ctx.send("{} you've been pardonned by {}.\t ({} slaps left)".format(member.mention, ctx.author.mention, slaps[str(ctx.guild.id)][str(member.id)]))

def setup(bot):
	bot.add_cog(Slapping(bot))