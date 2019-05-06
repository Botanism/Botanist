import logging
from settings import *
import discord
from checks import *



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
#				BotEssentials			#
#										#
#										#
#########################################
'''This cog contains all the basemost functions that all bots should contain.
See https://github.com/organic-bots/ForeBot for more information'''


class BotEssentials(commands.Cog):
	"""All of the essential methods all of our bots should have"""
	def __init__(self, bot):
		self.bot = bot
			
	@commands.Cog.listener()
	async def on_ready(self):
		print('We have logged in as {0.user}'.format(self.bot))

	@commands.Cog.listener()
	async def on_member_join(self, member):
		local_logger.info("User {0.name}[{0.id}] joined {1.name}[{1.id}]".format(member, member.guild))
		await member.guild.system_channel.send("Welcome to {} {}! Please make sure to take a look at our {} and before asking a question, at the {}".format(member.guild.name, member.mention, CHANNELS["rules"].mention, CHANNELS["faq"].mention))


	@commands.command()
	async def ping(self, ctx):
		'''This command responds with the current latency.'''
		latency = self.bot.latency
		await ctx.send("**Pong !** Latency of {0:.3f} seconds".format(latency))


	#Command that shuts down the bot
	@commands.command()
	@is_author()
	async def shutdown(self, ctx):
		print("Goodbye")
		local_logger.info("Switching to invisible mode")
		await self.bot.change_presence(status=discord.Status.offline)
		#time.sleep(0.1)
		await ctx.send("Goodbye")
		local_logger.info("Closing connection to discord")
		await self.bot.close()
		local_logger.info("Quitting python")
		await quit()


def setup(bot):
	bot.add_cog(BotEssentials(bot))