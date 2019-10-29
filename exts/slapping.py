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
	async def slap(self, ctx, member:discord.Member, *reason):
		'''Meant to give a warning to misbehavioring members. Cumulated slaps will result in warnings, role removal and eventually kick. Beware the slaps are loged throughout history and are cross-server'''
		if len(reason):
			reason_str=""
			for w in reason:
				reason_str+=f" {w}"
		else:
			reason_str= "of your behavior"

		with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
			#building audit log entry
			audit = f"{ctx.channel.id}/{ctx.message.id}"
			
			#updating dict
			if str(member.id) in slaps:
				slaps[str(member.id)].append(audit)			
			else:
				slaps[str(member.id)] = [audit]

			#warning
			await ctx.send(f"{member.mention} you've been slapped for the {len(slaps[str(member.id)])} time because of {reason_str}! Be careful, if you get slapped too much there *will* be consequences!")

	@commands.command()
	@is_init()
	@has_auth("manager")
	async def pardon(self, ctx, member:discord.Member, nbr=0):
		'''Pardonning a member to reduce his slap count'''

		with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
			s = slaps[str(member.id)]
			if nbr==0 or len(s)<nbr:
				slaps.pop(str(member.id))
			else:
				for i in range(nbr):
					slaps[str(member.id)].pop()

			await ctx.send(f"{ctx.message.author.name} has pardonned you for some of your mistakes {member.mention}.")

	@commands.command()
	@is_init()
	@has_auth("manager")
	async def slaps(self, ctx, *members:discord.Member):
		'''returns an embed representing the number of slaps of each member. More detailed info can be obtained if member arguments are provided.'''
		fields = []
		#a single string if there's no member argument
		if not len(members):fields = ""

		m_ids = [str(m.id) for m in members]
		
		with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
			for m in slaps:
				#checking member
				member = ctx.guild.get_member(int(m))
				if member==None: continue

				#building string for embed fields
				if len(members)==0:
					fields+=f"**{member.name}**: {len(slaps[m])}\n"

				elif m in m_ids:
					crt_str=""
					for s in slaps[m]:
						try:
							message = await self.bot.get_channel(int(s.split("/")[0])).fetch_message(int(s.split("/")[1]))
							#building reason
							reason = message.content.split(">", 1)[1][1:]
							if not reason: reason="**for no provided reason**"
							else: reason = f"because of {reason}"
						except discord.NotFound as e:
							reason = "**Message deleted**"


						#building string
						crt_str+=f"[Toude](https://discordapp.com/channels/{ctx.guild.id}/{s}) {reason}\n"
					fields.append({"name":member.name, "value":crt_str, "inline":False})

		#checking if a member has been slapped
		if not fields:
			await ctx.send("Congratulations! Your server is so full of respect that not a single member is slapped"+EMOJIS["tada"])
			return

		#if a user has been slapped
		embed = discord.Embed(
			title="Slaps "+EMOJIS["hammer"],
			description="The slapped users and their infraction(s)",
			colour=16753920) #used to be blurpple 7506394
		
		#adding fields
		if not len(members):
			embed.add_field(name="Members List", value=fields)

		else:
			for field in fields:
				embed.add_field(**field)

		await ctx.send(embed=embed)



def setup(bot):
	bot.add_cog(Slapping(bot))