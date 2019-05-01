import discord
from settings import *
from checks import *


class Poll(commands.Cog):
	"""TODO: A suite of commands providing users with tools to more easilly get the community's opinion on an idea"""
	def __init__(self, bot):
		self.bot = bot
		
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		'''currently makes this checks for ALL channels. Might want to change the behavior to allow reactions on other msgs'''

		#checking that user isn't the bot
		print(reaction.message.channel.name)
		if user != self.bot and (reaction.message.channel.name in POLL_ALLOWED_CHANNELS):

			#checking if reaction is allowed
			if reaction.emoji not in [EMOJIS["thumbsdown"],EMOJIS["thumbsup"],EMOJIS["shrug"]]:
				#deleting  reaction of the user. Preserves other reactions
				await reaction.remove(user)



	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author==self.bot.user: return

		if message.channel.name == "polls" and message.content.startswith(PREFIX)!=True:
			embed_poll = discord.Embed(
				title = "Do you agree ?",
				description = message.content,
				colour = discord.Color(7726379),
				url = None
				)

			#embed_poll.set_thumbnail(url=message.author.avatar_url)
			embed_poll.set_footer(text=message.author.name, icon_url=message.author.avatar_url)

			await message.delete()
			sent_msg = await message.channel.send(embed=embed_poll)
			await sent_msg.add_reaction(EMOJIS["thumbsup"])
			await sent_msg.add_reaction(EMOJIS["shrug"])
			await sent_msg.add_reaction(EMOJIS["thumbsdown"])

def setup(bot):
	bot.add_cog(Poll(bot))