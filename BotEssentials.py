import logging
from settings import *
import discord
from utilities import *
import json


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
	async def on_guild_join(self, guild):
		with open(f"{guild.id}.json", "w") as file:
			file.write(DEFAULT_SERVER_FILE)
		local_logger.info(f"Joined server {guild.name}")

			
	@commands.Cog.listener()
	async def on_ready(self):
		print('Logged in as {0.user}'.format(self.bot))
		local_logger.info('Logged in as {0.user}'.format(self.bot))

	@commands.Cog.listener()
	async def on_member_join(self, member):
		local_logger.info("User {0.name}[{0.id}] joined {1.name}[{1.id}]".format(member, member.guild))
		welcome_msg = get_conf(member.guild.id)["messages"]["welcome"]
		if welcome_msg != False:
			await member.guild.system_channel.send(welcome_msg.format(member.mention))

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		local_logger.info("User {0.name}[{0.id}] left {1.name}[{1.id}]".format(member, member.guild))
		goodbye_msg = get_conf(member.guild.id)["messages"]["goodbye"]
		if goodbye_msg != False:
			await member.guild.system_channel.send(goodbye_msg.format(member.mention))		

	@commands.command()
	async def ping(self, ctx):
		'''This command responds with the current latency.'''
		latency = self.bot.latency
		await ctx.send("**Pong !** Latency of {0:.3f} seconds".format(latency))

	#Command that shuts down the bot
	@commands.command()
	@is_runner()
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

	@commands.command()
	@has_auth("manager")
	async def clear(self, ctx, nbr:int):
		'''deletes specified <nbr> number of messages in the current channel'''
		to_del = []
		async for msg in ctx.channel.history(limit=nbr+1):
			local_logger.info("Deleting {}".format(msg))
			to_del.append(msg)

		try:
			await ctx.channel.delete_messages(to_del)
		except Exception as e:
			local_logger.exception("Couldn't delete at least on of{}".format(to_del))
			raise e

	@commands.command()
	async def status(self, ctx):
		stats = discord.Embed(name="Server Info", description=f"{ctx.guild.name} was created on {str(ctx.guild.created_at)[:10]} and belongs to {ctx.guild.owner.name}. Since then {ctx.guild.member_count-1} users have joined it.", color=7506394)
		stats.set_thumbnail(url=ctx.guild.icon_url)
		
		#member stats
		mstatus = {"online":0, "idle":0, "dnd":0, "offline":0}
		for member in ctx.guild.members:
			mstatus[str(member.status)]+=1
		#-> change to make use of custom emojis
		status_str = '{online} online\n{idle} idling\n{dnd} not to disturb\n{offline} offline'.format(**mstatus)
		stats.add_field(name=f"Member statistics", value=status_str, inline=False)

		#structure info
		rs = ctx.guild.roles
		rs.reverse()
		print(rs, type(rs))
		rs_str = ""
		for r in rs:
			rs_str+=f"{r.name}\n"
		struct_str = f"This server uses the {len(rs)} following roles:\n{rs_str}"
		stats.add_field(name="Server structure", value=struct_str, inline=False)
		await ctx.send(embed=stats)






def setup(bot):
	bot.add_cog(BotEssentials(bot))