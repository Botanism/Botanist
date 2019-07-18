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

	@commands.command()
	@is_init()
	@has_auth("manager")
	async def slap(self, ctx, member:discord.Member):
		'''Meant to give a warning to misbehavioring members. Cumulated slaps will result in warnings, role removal and eventually kick. Beware the slaps are loged throughout history and are cross-server'''
		#slapping
		with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER)[member.id] as slaps:
			slaps +=1
			#warning
			await ctx.send("{} you've been slapped by {} because of your behavior! This is the {} time. Be careful, if you get slapped too much there *will* be consequences !".format(member.mention, ctx.message.author.mention, slaps))

	@commands.command()
	@is_init()
	@has_auth("manager")
	async def pardon(self, ctx, member:discord.Member, nbr=0):
		'''Pardonning a member resets his slaps count.'''

		with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
			s = slaps[member.id]
			if nbr==0 or s<nbr:
				slaps.pop(member.id)
			else:
				s -=nbr

			await ctx.send("{} you've been pardonned by {}.\t ({} slaps left)".format(member.mention, ctx.author.mention, s))

	@commands.command()
	@is_init()
	@has_auth("manager")
	async def slaps(self, ctx):
		'''returns an embed representing the number of slaps of each member'''
		slaps_str = ""
		with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
			for m in slaps:
				member = ctx.guild.get_member(int(m))
				slaps_str+=f"**{member.name}**: {slaps[m]}\n"

		ctx.send(embed=discord.Embed(
			title="Slaps", description="The slapped users and the number of their infraction",
			colour=16776960))







def setup(bot):
	bot.add_cog(Slapping(bot))