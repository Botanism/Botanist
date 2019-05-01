import discord
from settings import *
from checks import *

class Embedding(commands.Cog):
	"""A suite of command providing users with embeds manipulation tools."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def embed(self, ctx, *args):
		"""allows you to post a message as an embed. Your msg will be reposted by the bot as an embed !"""
		if ctx.channel.name in POLL_ALLOWED_CHANNELS:
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