from settings import *
import discord
from checks import *

#########################################
#										#
#										#
#				BotEssentials			#
#										#
#										#
#########################################
'''This cog contains all basemost functions that all bots should contain.
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

		faq_channel = discord.utils.get(member.guild.channels, name="faq")
		rules_channel = discord.utils.get(member.guild.channels, name="rules")
		await member.guild.system_channel.send("Welcome to {} {}! Please make sure to take a look at our {} and before asking a question, at the {}".format(member.guild.name, member.mention, rules_channel.mention, faq_channel.mention))


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
		await self.bot.change_presence(status=discord.Status.offline)
		#time.sleep(0.1)
		await ctx.send("Goodbye")
		await self.bot.close()
		await quit()


def setup(bot):
	bot.add_cog(BotEssentials(bot))