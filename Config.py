import logging
import discord
import asyncio
import os
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
	@is_server_owner()
	async def cfg(self, ctx):
		self.ad_msg = "I ({}) have recently been added to this server ! I hope I'll be useful to you. I hope you won't find me too many bugs. However if you do I would appreciate it if you could report them to the server ({}) where my developers are ~~partying~~ working hard to make me better ! This is also the place to share your thoughts on how to improve me. Have a nice day and maybe, see you there {}".format(ctx.me.mention, DEV_SRV_URL, EMOJIS["wave"])
		if ctx.invoked_subcommand == None:
			await ctx.send(ERR_NO_SUBCOMMAND)


	@cfg.command()
	async def init(self, ctx):
		#creating new hidden channel only the owner can see
		overwrites = {
		ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
		ctx.guild.owner : discord.PermissionOverwrite(read_messages=True)
		}
		self.config_channels[ctx.guild.id] = await ctx.guild.create_text_channel("cli-bot-config")

		#making conf file if it doesn't exist
		if not was_init(ctx):
			#making config file
			with open(os.path.join(CONFIG_FOLDER, f"{ctx.guild.id}.json"), "w") as file:
				file.write(DEFAULT_SERVER_FILE)
			#making slapping file
			with open(os.path.join(SLAPPING_FOLDER, f"{ctx.guild.id}.json"), "w") as file:
				file.write(DEFAULT_SLAPPED_FILE)

		#starting all configurations
		await self.config_channels[ctx.guild.id].send(f'''You are about to start the configuration of {ctx.me.mention}. If you are unfamiliar with CLI (Command Line Interface) you may want to check the documentation on github ({WEBSITE}). The same goes if you don't know the bot's functionnalities\n*Starting full configuration...*''')
		await self.config_channels[ctx.guild.id].send("This will overwrite all of your existing configurations. Do you want to continue ? [y/n]")
		response = await self.bot.wait_for("message", check=self.is_yn_answer)
		if response.content[0].lower() == "n":return False
		await self.config_channels[ctx.guild.id].send("**Starting full bot configuration...**")

		try:
			await self.cfg_poll(ctx)
			await self.config_channels[ctx.guild.id].send("Role setup is **mendatory** for the bot to work correctly. Otherise no one will be able to use administration commands.")
			await self.cfg_role(ctx)
			await self.cfg_welcome(ctx)
			await self.cfg_goodbye(ctx)
			await self.cfg_todo(ctx)

			#asking for permisison to advertise
			await self.config_channels[ctx.guild.id].send("You're almost done ! Just one more thing...")
			await self.allow_ad(ctx)


			local_logger.info(f"Setup for server {ctx.guild.name}({ctx.guild.id}) is done")

		except Exception as e:
			await ctx.send(ERR_UNEXCPECTED.format(None))
			await ctx.send("Dropping configuration and rolling back unconfirmed changes.")
			#await self.config_channels[ctx.guild.id].delete(reason="Failed to interactively configure the bot")
			local_logger.exception(e)

		finally:
			await self.config_channels[ctx.guild.id].send("Thank you for inviting our bot and taking the patience to configure it.\nThis channel will be deleted in 10 seconds...")
			await asyncio.sleep(10)
			await self.config_channels[ctx.guild.id].delete(reason="Configuration completed")



	@cfg.command()
	@is_init()
	async def chg(self, ctx, setting):
		try:
			eval("self.cfg_"+setting)

		except Exception as e:
			local_logger.exception(e)


	def is_yn_answer(self, ctx):
		if (ctx.channel == self.config_channels[ctx.guild.id]) and ((ctx.content.lower() in self.allowed_answers[0]) or (ctx.content.lower() in self.allowed_answers[1])): return True
		return False

	def is_answer(self, ctx):
		if ctx.channel == self.config_channels[ctx.guild.id]: return True
		return False


	async def cfg_poll(self, ctx):
		try:
			await self.config_channels[ctx.guild.id].send("**Starting poll configuration**")
			await self.config_channels[ctx.guild.id].send("Do you want to activate polls on this server ? [y/n]")
			#awaiting the user response
			response = await self.bot.wait_for("message", check=self.is_yn_answer)
			if not response.content[0].lower() == "y": return False

			retry = True
			while retry:
				#getting the list of channels to be marked polls
				await self.config_channels[ctx.guild.id].send(f"List all the channels you want to use as poll channels. You must mention those channels like this: {self.config_channels[ctx.guild.id].mention}")
				response = await self.bot.wait_for("message", check=self.is_answer)
				poll_channels = response.channel_mentions
				if self.config_channels[ctx.guild.id] in poll_channels:
					await self.config_channels[ctx.guild.id].send("You cannot set this channel as a poll one for safety reasons. Please try again...")
					continue

				
				#building string with all the channels that will be marked for polls
				poll_channels_str = ""
				for chan in poll_channels:
					poll_channels_str+= " "+chan.mention

				await self.config_channels[ctx.guild.id].send(f"You are about to make {poll_channels_str} poll channels. Do you want to continue? [y/n]")

				response = await self.bot.wait_for("message", check=self.is_yn_answer)
				#wether the asnwer was positive
				if not response.content[0].lower() =="y":
					#making sure the user really wants to cancel poll configuration
					await self.config_channels[ctx.guild.id].send("Aborting addition of poll channels. Do you want to leave the poll configuration interface ? [y/n]")
					response = await self.bot.wait_for("message", check=self.is_yn_answer)
					if response.content[0].lower()=="y":
						local_logger.info(f"Poll configuration has been cancelled for server {ctx.guild.name}")
						retry = False

				else: retry=False

			poll_channels_ids = []
			for chan in poll_channels:
				poll_channels_ids.append(chan.id)


			old_conf = get_conf(ctx.guild.id)
			old_conf["poll_channels"] = poll_channels_ids

			if update_conf(ctx.guild.id, old_conf) == False:
				await self.config_channels[ctx.guild.id].send(ERR_UNEXCPECTED)

			else:
				await self.config_channels[ctx.guild.id].send("Poll configuration is done.")


			local_logger.info(f"Configuration of poll for server {ctx.guild.name} ({ctx.guild.id}) has been completed.")

		except Exception as e:
			local_logger.exception(e)
			raise e


	async def cfg_role(self, ctx):
		try:
			#introducing the clearance levels the bot uses
			await self.config_channels[ctx.guild.id].send("**Starting role configuration**\nThis bot uses two level of clearance for its commands.\nThe first one is the **manager** level of clearance. Everyone with a role with this clearance can use commands related to server management. This includes but is not limited to message management and issuing warnings.\nThe second level of clearance is **admin**. Anyone who has a role with this level of clearance can use all commands but the ones related to the bot configuration. This is reserved to the server owner. All roles with this level of clearance inherit **manager** clearance as well.")

			new_roles = []
			for role_lvl in ROLES_LEVEL:
				retry = True
				while retry:
					new_role = []
					#asking the owner which roles he wants to give clearance to
					await self.config_channels[ctx.guild.id].send(f"List all the roles you want to be given the **{role_lvl}** level of clearance.")
					response = await self.bot.wait_for("message", check=self.is_answer)
					roles = response.role_mentions
					if len(roles) == 0:
						await self.config_channels[ctx.guild.id].send(f"You need to set at least one role for the {role_lvl} clearance.")
						continue

					#building roll string
					roles_str = ""
					for role in roles:
						roles_str+= f" {role.mention}"

					#asking for confirmation
					await self.config_channels[ctx.guild.id].send(f"You are about to give{roles_str} roles the **{role_lvl}** level of clearance. Do you confirm this ? [y/n]")
					response = await self.bot.wait_for("message", check=self.is_yn_answer)
					if response.content[0].lower() == "n":
						await self.config_channels[ctx.guild.id].send(f"Aborting configuration of {role_lvl}. Do you want to retry? [y/n]")
						response = await self.bot.wait_for("message", check=self.is_yn_answer)
						if response.content[0].lower() == "n":
							local_logger.info(f"The configuration for the {role_lvl} clearance has been cancelled for server {ctx.guild.name}")
							retry = False

					else: retry = False


				local_logger.info(f"Server {ctx.guild.name} configured its {role_lvl} roles")

				for role in roles:
					new_role.append(role.id)

				#adding to master role list
				new_roles.append(new_role)


			#giving admin roles the manager clearance
			for m_role in new_roles[1]:
				new_roles[0].append(m_role)

			old_conf = get_conf(ctx.guild.id)

			#updating the values
			old_conf["roles"]["manager"] = new_roles[0]
			old_conf["roles"]["admin"] = new_roles[1]

			if update_conf(ctx.guild.id, old_conf) == False:
				await self.config_channels[ctx.guild.id].send(ERR_UNEXCPECTED)

			else:
				await self.config_channels[ctx.guild.id].send("Successfully updated role configuration")


		except Exception as e:
			local_logger.exception(e)
			raise e


	async def cfg_welcome(self, ctx):
		try:
			await self.config_channels[ctx.guild.id].send("**Starting welcome message configuration**")
			retry = True

			await self.config_channels[ctx.guild.id].send("Do you want to have a welcome message sent when a new user joins the server ? [y/n]")

			response = await self.bot.wait_for("message", check=self.is_yn_answer)
			if response.content[0].lower() == "n":
				message = False
				retry = False

			while retry:

				await self.config_channels[ctx.guild.id].send("Enter the message you'd like to be sent to the new users. If you want to mention them use `{0}`")

				message = await self.bot.wait_for("message", check=self.is_answer)

				await self.config_channels[ctx.guild.id].send("To make sure the message is as you'd like I'm sending it to you.\n**-- Beginning of message --**")
				await self.config_channels[ctx.guild.id].send(message.content.format(ctx.guild.owner.mention))

				await self.config_channels[ctx.guild.id].send("**--End of message --**\nIs this the message you want to set as the welcome message ? [y/n]")
				response = await self.bot.wait_for("message", check=self.is_yn_answer)

				#the user has made a mistake
				if response.content[0].lower() == "n":
					await self.config_channels[ctx.guild.id].send("Do you want to retry ? [y/n]")
					response = await self.bot.wait_for("message", check=self.is_yn_answer)
					if response.content[0].lower == "n":
						message = False
						retry = False
					#otherwise retry
					continue

				else: retry = False

			if message != False:
				old_conf = get_conf(ctx.guild.id)
				old_conf["messages"]["welcome"]= message.content

				if update_conf(ctx.guild.id, old_conf) == False:
					await self.config_channels[ctx.guild.id].send(ERR_CANT_SAVE)


		except Exception as e:
			local_logger.exception(e)
			raise e


	async def cfg_goodbye(self, ctx):
		try:
			await self.config_channels[ctx.guild.id].send("**Starting goodbye message configuration**")
			retry = True

			await self.config_channels[ctx.guild.id].send("Do you want to have a goodbye message sent when an user leaves the server ? [y/n]")

			response = await self.bot.wait_for("message", check=self.is_yn_answer)
			if response.content[0].lower() == "n":
				message = False
				retry = False

			while retry:

				await self.config_channels[ctx.guild.id].send("Enter the message you'd like to be sent. If you want to mention them use `{0}`")

				message = await self.bot.wait_for("message", check=self.is_answer)

				await self.config_channels[ctx.guild.id].send("To make sure the message is as you'd like I'm sending it to you. Enventual mentions will be directed to you.\n**-- Beginning of message --**")
				await self.config_channels[ctx.guild.id].send(message.content.format(ctx.guild.owner.mention))

				await self.config_channels[ctx.guild.id].send("**--End of message --**\nIs this the message you want to set as the goodbye message ? [y/n]")
				response = await self.bot.wait_for("message", check=self.is_yn_answer)

				#the user has made a mistake
				if response.content[0].lower() == "n":
					await self.config_channels[ctx.guild.id].send("Do you want to retry ? [y/n]")
					response = await self.bot.wait_for("message", check=self.is_yn_answer)
					if response.content[0].lower == "n":
						message = False
						retry = False
					#otherwise retry
					continue
				else: retry = False

			if message != False:
				old_conf = get_conf(ctx.guild.id)
				old_conf["messages"]["goodbye"]= message.content

				if update_conf(ctx.guild.id, old_conf) == False:
					await self.config_channels[ctx.guild.id].send(ERR_CANT_SAVE)



		except Exception as e:
			local_logger.exception(e)
			raise e

	async def allow_ad(self, ctx):
		try:
			await self.config_channels[ctx.guild.id].send("Do you allow me to send a message in a channel of your choice ? This message would give out a link to my development server. It would allow me to get more feedback. This would really help me pursue the development of the bot. If you like it please think about it (you can always change this later). [y/n]")
			response = await self.bot.wait_for("message", check=self.is_yn_answer)
			if response.content[0].lower()=="n": return False

			await self.config_channels[ctx.guild.id].send("Thank you very much ! In which channel do you want me to post this message ?")
			response = await self.bot.wait_for("message", check=self.is_answer)

			old_conf = get_conf(ctx.guild.id)
			old_conf["advertisement"] = response.channel_mentions[0].id

			chan = discord.utils.find(lambda c: c.id==old_conf["advertisement"], ctx.guild.channels)
			await chan.send(self.ad_msg)

			#updating conf
			update_conf(ctx.guild.id, old_conf)



		except Exception as e:
			local_logger.exception(e)
			raise e


	@cfg.command()
	async def leave(self, ctx):
		ctx.send("You are about to remove the bot from the server. This will erase all of your configuration from the mainframe and you won't be able to recover the bot without getting another invite. Are you sure you want to continue ? (y/N)")

	@cfg.command()
	async def cfg_todo(self, ctx):
			await self.config_channels[ctx.guild.id].send("You are entering the Todo extension configuration. This extension lets you manage a todo list directly from discord. This extension requires more configuration than most. It has thus been subdivided for you. I'm going to ask which parts you want me to configure with you...")

			#asking for group configuration
			await self.config_channels[ctx.guild.id].send("Do you want to configure the todo groups ?")
			reponse = await self.bot.wait_for("message", check=self.is_yn_answer)
				if response.content[0].lower() == "y": self.cfg_todo_grps(ctx)

			#asking for channel configuration
			await self.config_channels[ctx.guild.id].send("Do you want to configure the todo channels ?")
			reponse = await self.bot.wait_for("message", check=self.is_yn_answer)
				if response.content[0].lower() == "y": self.cfg_todo_chan(ctx)

			#asking for type configuration
			#await self.config_channels[ctx.guild.id].send("Do you want to configure the todo types ?")
			#reponse = await self.bot.wait_for("message", check=self.is_yn_answer)
			#	if response.content[0].lower() == "y": self.cfg_todo_type(ctx)

	async def cfg_todo_grps(self, ctx):
		try:
			retry = True
			groups = []
			while retry:
				await self.config_channels[ctx.guild.id].send("What is the name of the group you want to make ?")
				response = await self.bot.wait_for("message", check=self.is_answer)

				await self.config_channels[ctx.guild.id].send("About to create group {}. Do you want to confirm this?")
				response = await self.bot.wait_for("message", check=self.is_yn_answer)
				if response.content[0].lower() == "n":
					continue

				#if the creation was successfull
				await self.config_channels[ctx.guild.id].send("Do you want to create another group ? [y/n]")
				response =  await self.bot.wait_for("message", check=self.is_yn_answer)
				if response.content[0].lower() == "n":
					retry = False
					continue

			#building group string and making the group
			grps_str = ""
			todo_dict = get_todo(ctx.guild.id)
			for grp in groups:
				#building the string
				grps_str+=f"`{grp}`, "

				#making the group
				todo_dict["groups"][grp] = []

			update_todo(ctx.guild.id, todo_dict)

			await self.config_channels[ctx.guild.id].send(f"You created the following groups: {grps_str}")

		except Exception as e:
			local_logger.exception(e)
			raise e



	async def cfg_todo_chan(self, ctx):
		try:
			await self.config_channels[ctx.guild.id].send("Each group you've set earlier can be attached to several channels. Each time a new entry is made for a group, the todo will be posted in every channel bound to it.")
			todo_dict = get_todo(ctx.guild.id)
			for group in todo_dict["groups"]:
				retry = True
				while retry:
					await self.config_channels[ctx.guild.id].send(f"List (like this {self.config_channels[ctx.guild.id].mention})all the channels you want to bind to the {group} group.")
					respone = await self.bot.wait_for("message", check=self.is_answer)

					#making group's channels
					chans = []
					chans_str = ""
					for chan in response.channel_mentions:
						chans_str+= f"{chan} "
						chans.append(chan)
					await self.config_channels[ctx.guild.id].send(f"You are about to make {chans_str} {group} todo channels. Do you want to confirm? [y/n]")
					response = await self.bot.wait_for("message", check=self.is_yn_answer)
					if response.content[0].lower() == "n":
						await self.config_channels[ctx.guild.id].send(f"Do you want to try to configure {group} again ?")
						response = await self.bot.wait_for("message", check=self.is_yn_answer)
						if response.content[0].lower() == "n":retry = False
						continue
					todo_dict["groups"][group] = chans

			await self.config_channels[ctx.guild.id].send("You are now done completing the configuration of the todo channels.")







		except Exception as e:
			local_logger.exception(e)
			raise e

	async def cfg_todo_type(self, ctx):
		try:
			retry = True
			while retry:
				await self.config_channels[ctx.guild.id].send("You are starting the todo types configuration. Which types do you want to add ? Write it like this: `my_type_name;ffffff` The part after the ")



		except Exception as e:
			local_logger.exception(e)
			raise e

					




def setup(bot):
	bot.add_cog(Config(bot))