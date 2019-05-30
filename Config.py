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



class Config(commands.Cog):
	"""a suite of commands meant ot give server admins/owners and easy way to setup the bot's
	preferences directly from discord."""
	def __init__(self, bot):
		self.bot = bot
		#change to make it cross-server
		self.config_channel=None

		#other values can't be added as of now
		self.allowed_answers = {1:["yes", "y"],
								0:["no", "n"]}



	@commands.group()
	@commands.is_owner()
	async def cfg(self, ctx):
		if ctx.invoked_subcommand == None:
			ctx.send(ERROR_NO_SUBCOMMAND)

	@cfg.command()
	async def init(self, ctx):
		#creating new hidden channel only the owner can see
		overwrites = {
		ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
		ctx.guild.owner : discord.PermissionOverwrite(read_messages=True)
		}
		self.config_channel = await ctx.guild.create_text_channel("cli-bot-config")

		#starting all configurations
		await ctx.send(f'''You are about to start the configuration of {ctx.me.mention}. If you are unfamiliar with CLI (Command Line Interface) you may want to check the documentation on github ({WEBSITE}). The same goes if you don't know the bot's functionnalities\n*Starting full configuration...*''')
		
		try:
			await self.cfg_poll(ctx)
			local_logger.info("Setup is done")

		except Exception as e:
			await ctx.send(ERR_UNEXCPECTED.format(None))
			await ctx.send("Dropping cofiguration and rolling back unconfirmed changes.")
			#await self.config_channel.delete(reason="Failed to interactively configure the bot")
			local_logger.exception(e)




	async def chg(self, ctx, setting):
		try:
			eval("self.chg_"+setting)

		except Exception as e:
			local_logger.exception(e)


	async def is_yn_answer(self, ctx):
		if (ctx.channel == self.config_channel) and (ctx.content in (self.allowed_answers[0] or self.allowed_answers[1])): return True
		return False

	async def is_answer(self, ctx):
		if ctx.channel == self.config_channel: return True
		return False

	@cfg.command()
	async def leave(self, ctx):
		ctx.send("You are about to remove the bot from the server. This will erase all of your configuration from the mainframe and you won't be able to recover the bot without getting another invite. Are you sure you want to continue ? (y/N)")

	async def cfg_poll(self, ctx):
		try:
			await self.config_channel.send("**Starting poll configuration**")
			await self.config_channel.send("Do you want to activate polls on this server ? [yes/no]")
			#awaiting the user response
			response = await self.bot.wait_for("message", check=self.is_yn_answer)
			if not response.content[0].lower() =="y": return False

			await self.config_channel.send("List all the channels you want to use as poll channels. Only put the channel mentions in your answer")
			response = await self.bot.wait_for("message", check=self.is_answer)
			poll_channels = response.channel_mentions
			local_logger.info((response.channel_mentions, "which makes", poll_channels))
			poll_channels_str = ""
			for chan in response.channel_mentions:
				poll_channels_str+= " "+chan.mention

			await self.config_channel.send(f"You are about to make {poll_channels_str} poll channels. Do you want to continue? [y/n]")

			response = await self.bot.wait_for("message", check=self.is_yn_answer)
			if not response.content[0].lower() =="y": return False

			#making the data to be saved
			with open(POLL_ALLOWED_CHANNELS_FILE, "r") as file:
				to_write = []
				for line in file.readlines():
					'''the file is organized like this:
					guild_id;poll_chan_1_id;poll_chan_2_id;\n'''
					segments = line.split(";")
					if not segments[0]==ctx.guild.id:
						to_write.append(line)

				guild_chans = f"{ctx.guild.id};"
				for chan in response.channel_mentions:
					guild_chans+= f"{chan.id};"
				guild_chans+="\n"

				to_write.append(guild_chans)

			#writting to the file
			write_str = ""
			for line in to_write:
				write_str+=line
			with open(POLL_ALLOWED_CHANNELS_FILE, "w") as file:
				file.write(write_str)

			await self.config_channel.send("Poll configuration is done.")





			local_logger.info(response)

		except Exception as e:
			local_logger.exception(e)




	async def cfg_roll(self, ctx):
		pass

	async def cfg_todo(self, ctx):
		pass

	async def cfg_welcome(self, ctx):
		pass

	async def yes_no_answer(self, ctx):
		pass


def setup(bot):
	bot.add_cog(Config(bot))