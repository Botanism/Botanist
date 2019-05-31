import logging
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


class Slapping(commands.Cog):
	"""a suite of commands meant to help moderators handle the server"""
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command()
	@commands.has_any_role(*GESTION_ROLES)
	async def slap(self, ctx, member:discord.Member):
		'''Meant to give a warning to misbehavioring members. Cumulated slaps will result in warnings, role removal and eventually kick. Beware the slaps are loged throughout history and are cross-server'''
		to_write = ""
		slap_count=0

		#reads the file and prepares logging of slaps
		with open(SLAPPED_LOG_FILE, "r") as file:
			content = file.readlines()
			for line in content:
				#finding the right server
				if line.startswith(str(ctx.guild.id)):
					#looking for the user in the guild slaps log
					guild_line = ""
					for user in line.split(";")[:1]:
						#whether the user if the member
						if int(user.split("|")[0]) == member.id:
							slap_count = int(user.split("|")[1])+1
							guild_line+=f"{member.id}|{slap_count};"
							continue

						#if the user does not match
						guild_line+=user

					#if the user wasn't found
					if slap_count==0:
						guild_line+=f"{member.id}|1;"

					#removing the last ";" and appending a line return
					to_write+=guild_line[-1]+"\n"

				else:
					to_write += line


		await ctx.send("{} you've been slapped by {} because of your behavior! This is the {} time. Be careful, if you get slapped too much there *will* be consequences !".format(member.mention, ctx.message.author.mention, slap_count))

		#writes out updated data to the file
		with open(SLAPPED_LOG_FILE, "w") as file:
			file.write(to_write)			

	@commands.command()
	@commands.has_any_role(*GESTION_ROLES)
	async def pardon(self, ctx, member:discord.Member, nbr=0):
		'''Pardonning a member resets his slaps count.'''
		to_write = ""
		nbr = int(nbr)

		#reads the file and prepares logging of slaps
		with open(SLAPPED_LOG_FILE, "r") as file:
			for line in file.readlines():
				if not line.startswith(str(ctx.guild.id)):
					to_write+=line
					continue

				#looking for the user
				guild_line = ""
				for user in line.split(";")[:1]:
					#whether the user is member
					if int(user.split("|")[0]) == member.id:
						local_logger.info(f"Found user {member.name} who has ot be pardonnned")
						crt_slaps = int(user.split("|")[1])
						#pardonnning the user
						if crt_slaps<nbr or nbr==0:
							crt_slaps =0

						else:
							crt_slaps-=nbr

						local_logger.info(f"{member.name} now has been slapped {crt_slaps} times")
						guild_line+=f"{member.id}|{crt_slaps};"

						continue

					#if the user isn't the right one
					guild_line+=user

				#removing the last ";" and appending a line return
				to_write+=guild_line[-1]+"\n"				




		#writting updated file
		with open(SLAPPED_LOG_FILE, "w") as file:
			file.write(to_write)

		local_logger.info("Pardonned {0.name}[{0.id}]".format(member))
		await ctx.send("{} you've been pardonned by {}.\t ({} slaps left)".format(member.mention, ctx.author.mention, crt_slaps))

def setup(bot):
	bot.add_cog(Slapping(bot))