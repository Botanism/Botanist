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
		self.config_channels={}

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
		self.config_channels[ctx.guild.id] = await ctx.guild.create_text_channel("cli-bot-config")

		#starting all configurations
		await self.config_channels[ctx.guild.id].send(f'''You are about to start the configuration of {ctx.me.mention}. If you are unfamiliar with CLI (Command Line Interface) you may want to check the documentation on github ({WEBSITE}). The same goes if you don't know the bot's functionnalities\n*Starting full configuration...*''')
		await self.config_channels[ctx.guild.id].send("This will overwrite all of your existing configurations. Do you want to continue ? [y/n]")
		response = self.bot.wait_for("message", check=self.is_yn_answer)
		if response[0].lower() == "n":return False
		await self.config_channels[ctx.guild.id].send("**Starting full bot configuration...**")

		try:
			await self.cfg_poll(ctx)
			await self.config_channels[ctx.guild.id].send("Role setup is **mendatory** for the bot to work correctly. Otherise no one will be able to use administration commands.")
			await self.cfg_roll(ctx)

			local_logger.info(f"Setup for server {ctx.guild.name}({ctx.guild.id}) is done")

		except Exception as e:
			await ctx.send(ERR_UNEXCPECTED.format(None))
			await ctx.send("Dropping configuration and rolling back unconfirmed changes.")
			#await self.config_channels[ctx.guild.id].delete(reason="Failed to interactively configure the bot")
			local_logger.exception(e)


	async def chg(self, ctx, setting):
		try:
			eval("self.chg_"+setting)

		except Exception as e:
			local_logger.exception(e)


	async def is_yn_answer(self, ctx):
		if (ctx.channel == self.config_channels[ctx.guild.id]) and (ctx.content in (self.allowed_answers[0] or self.allowed_answers[1])): return True
		return False

	async def is_answer(self, ctx):
		if ctx.channel == self.config_channels[ctx.guild.id]: return True
		return False


	async def cfg_poll(self, ctx):
		try:
			await self.config_channels[ctx.guild.id].send("**Starting poll configuration**")
			await self.config_channels[ctx.guild.id].send("Do you want to activate polls on this server ? [yes/no]")
			#awaiting the user response
			response = await self.bot.wait_for("message", check=self.is_yn_answer)
			if not response.content[0].lower() =="y": return False

			retry = True
			while retry:
				#getting the list of channels to be marked polls
				await self.config_channels[ctx.guild.id].send("List all the channels you want to use as poll channels.")
				response = await self.bot.wait_for("message", check=self.is_answer)
				poll_channels = response.channel_mentions
				
				#building string with all the channels that will be marked for polls
				poll_channels_str = ""
				for chan in response.channel_mentions:
					poll_channels_str+= " "+chan.mention

				await self.config_channels[ctx.guild.id].send(f"You are about to make {poll_channels_str} poll channels. Do you want to continue? [y/n]")

				response = await self.bot.wait_for("message", check=self.is_yn_answer)
				#wether the asnwer was positive
				if not response.content[0].lower() =="y":
					#making sure the user really wants to cancel poll configuration
					self.config_channels[ctx.guild.id].send("Aborting addition of poll channels. Do you want to leave the poll configuration interface ? [y/n]")
					response = await self.bot.wait_for("message", check=self.is_yn_answer)
					if response.content[0].lower()=="y":
						local_logger.info(f"Poll configuration has been cancelled for server {ctx.guild.name}")
						retry = False


			#making the data to be saved
			with open(POLL_ALLOWED_CHANNELS_FILE, "r") as file:
				to_write = []
				for line in file.readlines():
					'''the file is organized like this:
					\nguild_id;poll_chan_1_id;poll_chan_2_id;'''
					segments = line.split(";")
					if not int(segments[0])==ctx.guild.id:
						to_write.append(line)

				guild_chans = f"{ctx.guild.id};"
				for chan in poll_channels:
					guild_chans+= f"{chan.id};"

				#removing the last ";" to prevent Poll from trying to convert it to an int
				guild_chans = guild_chans[:-1] + "\n"

				to_write.append(guild_chans)
				local_logger.info(str(guild_chans))

			#writting to the file
			write_str = ""
			for line in to_write:
				write_str+=line

			local_logger.info(write_str)
			with open(POLL_ALLOWED_CHANNELS_FILE, "w") as file:
				file.write(write_str)

			await self.config_channels[ctx.guild.id].send("Poll configuration is done.")


			local_logger.info(f"Configuration of poll for server {ctx.guild.name} ({ctx.guild.id}) has been completed.")

		except Exception as e:
			local_logger.exception(e)


	async def cfg_roll(self, ctx):
		try:
			#introducing the clearance levels the bot uses
			await self.config_channels[ctx.guild.id].send("**Starting role configuration**")
			await self.config_channels[ctx.guild.ig].send("This bot uses two level of clearance for its commands.")
			await self.config_channels[ctx.guild.ig].send("The first one is the **manager** level of clearance. Everyone with a role with this clearance can use commands related to server management. This includes but is not limited to message management and issuing warnings.")
			await self.config_channels[ctx.guild.ig].send("The second level of clearance is **admin**. Anyonw who has a role with this level of clearance can use all commands but the ones related to the bot configuration. This is reserved to the server owner. All roles with this level of clearance inherit **manager** clearance as well.")

			new_roles = []
			for role_lvl in ROLES_LEVEL:
				new_role = []
				#asking the owner which roles he wants to give clearance to
				await self.config_channels[ctx.guild.ig].send(f"List all the roles you want to be given the **{role_lvl}** level of clearance.")
				response = self.bot.wait_for("message", check=self.is_answer)
				roles = response.role_mentions

				#building roll string
				roles_str = ""
				for role in roles:
					roles_str+= f" {role}"

				#asking for confirmation
				await self.config_channels[ctx.guild.id].send(f"You are about to give{roles_str} roles the **{role_lvl}** level of clearance. Do you confirm this ? [y/n]")
				response = self.bot.wait_for("message", check=self.is_yn_answer)
				if repsonse[0].lower() == "n": return False
				local_logger.info(f"Server {ctx.guild.name} configured its {role_lvl} roles")

				for role in roles:
					new_role.append(role.id)

			#writting configuration to file
			with open(ROLES_FILE, "r") as file:
				'''the file is written like this:
				guild_id;management_role_1|management_role_2;admin_role_1|admin_role_2'''
				for line in file.readlines():
					segments = line.split(";")
					to_write = ""
					if int(segments[0]) == ctx.guild.id:
						continue
					#if the line isn't defining the server's role settings, marking it for rewrite
					to_write += line

			#building the roles lists
			for m_role in new_roles[0]:
				new_roles[1].append(m_role)

			#adding management roles
			guild_line = f"{ctx.guild.id};"
			for role in new_roles[0]:
				guild_line += f"{role};"

			#adding weak seperator
			guild_line+="|"

			#adding admin roles
			for role in new_roles[1]:
				guild_line += f"{role};"




		except Exception as e:
			local_logger.exception(e)
			raise e







	async def cfg_todo(self, ctx):
		pass

	async def cfg_welcome(self, ctx):
		pass


	@cfg.command()
	async def leave(self, ctx):
		ctx.send("You are about to remove the bot from the server. This will erase all of your configuration from the mainframe and you won't be able to recover the bot without getting another invite. Are you sure you want to continue ? (y/N)")




def setup(bot):
	bot.add_cog(Config(bot))