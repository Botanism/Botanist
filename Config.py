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



class Config(commands.Cog):
	"""a suite of commands meant ot give server admins/owners and easy way to setup the bot's
	preferences directly from discord."""
	def __init__(self, bot):
		self.bot = bot
	
	@commands.group()
	@is_owner()
	async def cfg(self, ctx):
		if invoked_subcommand == None:
			ctx.send(ERROR_NO_SUBCOMMAND)

	@cfg.command()
	async def init(self, ctx):
		pass

	@cfg.command()
	async def chg(self, ctx, setting):
		try:
			eval("self.chg_"+setting)

		except Exception as e:
			local_logger.exception(ERR_UNEXCPECTED)

	@cfg.command()
	async def leave(self, ctx)-> int:
		ctx.send("You are about to remove the bot from the server. This will erase all of your configuration from the mainframe and you won't be able to recover the bot without getting another invite. Are you sure you want to continue ? (y/N)")

	async def cfg_poll(self, ctx):
		pass

	async def cfg_roll(self, ctx):
		pass

	async def cfg_todo(self, ctx):
		pass

	async def cfg_welcome(self, ctx):
		pass

	async def yes_no_answer(self, ctx):
		pass

	@commands.Cog.listener()
	#is it possible to add checks to listeners ? (is_owner and in_channel)
	async def on_message(self, message):
		
		#checking that the msg isn't from the bot, in the cfg channel and from the guild owner
		#change with a list of IDs that represent the in-progress configuration channels
		if self.message.name!="foreman-configuration-channel": return
		if message.author==self.bot.user: return
		#is it possible to add a check inside a code block ?
		if message.author != message.guild.owner: return



def setup(bot):
	bot.add_cog(Poll(bot))