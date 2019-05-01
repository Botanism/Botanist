from settings import *
import discord
from checks import *

class Role(commands.Cog):
	"""role management utility. Requires a Gestion role"""
	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	@commands.has_any_role(*GESTION_ROLES)
	async def role(self, ctx):
		'''role management utility. Requires a Gestion role'''
		if ctx.invoked_subcommand is None:
			await ctx.send("NotEnoughArguments:\tYou must provide a subcommand")

	@role.command()
	async def add(self, ctx, member: discord.Member, *roles:discord.Role):
		'''adds role(s) to <member>'''
		#print("role:\t{} will be added to {}".format(roles, member))
		if len(role)==0:
			await ctx.send("NotEnoughArguments:\tYou must provide at least one `role`")

		else:
			try:
				await member.add_roles(*roles)
			except Exception as e:
				await ctx.send("An unexpected error occured !\nTraceback:```python\n{}```".format(e))

	@role.command()
	async def rm(self, ctx, member:discord.Member, *roles:discord.Role):
		'''removes role(s) to <member>'''
		if len(role)==0:
			await ctx.send("NotEnoughArguments:\tYou must provide at least one `role`")

		else:
			try:
				await member.remove_roles(*roles)
			except Exception as e:
				await ctx.send("An unexpected error occured !\nTraceback:```python\n{}```".format(e))


def setup(bot):
	bot.add_cog(Role(bot))