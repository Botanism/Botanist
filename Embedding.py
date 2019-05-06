import logging
import discord
from settings import *
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
#			Making commands				#
#										#
#										#
#########################################


class Embedding(commands.Cog):
	"""A suite of command providing users with embeds manipulation tools."""
	def __init__(self, bot):
		self.bot = bot
		#making poll_allowed channels according to the message's guild
		self.poll_allowed_chans = {}
		with open(POLL_ALLOWED_CHANNELS_FILE) as file:
			for line in file.readlines():
				self.poll_allowed_chans[line.split(";")[0]] = [chan_id for chan_id in line.split(";")[1:]]


	@commands.command()
	async def embed(self, ctx, *args):
		"""allows you to post a message as an embed. Your msg will be reposted by the bot as an embed !"""
		if ctx.channel.name in self.poll_allowed_chans:
			local_logger.info("Preventing user from making an embed in a poll channel")
			await ctx.message.delete()
			return

		msg = ""
		for arg in args:
			msg += " {}".format(arg)

		embed_msg = discord.Embed(
				title = None,
				description = msg,
				colour = ctx.author.color,
				url = None
				)

		embed_msg.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)

		await ctx.message.delete()
		await ctx.message.channel.send(embed=embed_msg)

def setup(bot):
	bot.add_cog(Embedding(bot))