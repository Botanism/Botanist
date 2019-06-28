import logging
import discord
import io
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


class Embedding(commands.Cog):
	"""A suite of command providing users with embeds manipulation tools."""
	def __init__(self, bot):
		self.bot = bot
		#maybe think to block sending an embed in a poll channel

	@commands.command()
	async def embed(self, ctx, *args):
		"""allows you to post a message as an embed. Your msg will be reposted by the bot as an embed !"""
		if ctx.channel.id in get_poll_chans(ctx.guild.id):
			local_logger.info("Preventing user from making an embed in a poll channel")
			await ctx.message.delete()
			return

		#lining attachements
		files = []
		for attachment in ctx.message.attachments:
			content = await attachment.read()
			io_content = io.BytesIO(content)
			file = discord.File(io_content, filename=attachment.filename)
			files.append(file)

		embed_msg = discord.Embed(
				title = None,
				description = ctx.message.content[8:],
				colour = ctx.author.color,
				url = None
				)
		embed_msg.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)

		await ctx.message.delete()
		await ctx.message.channel.send(embed=embed_msg, files=files)

def setup(bot):
	bot.add_cog(Embedding(bot))