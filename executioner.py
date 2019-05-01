#!/usr/bin/env python3

import discord
from discord.ext import commands
from discord.utils import find as dfind
import math
import requests as rq
from bs4 import BeautifulSoup
import time
import random

#########################################
#										#
#										#
#			Global Variables			#
#										#
#										#
#########################################


PREFIX = "::"
TOKEN = "NTYzODQ4MDcxMjE0MjY4NDI5.XMjofQ.c0Chs2b0q4Wjp2yqh3MuWfhDU0M"
AUTHOR_ID=289426079544901633

#can be both str and discord snowflake IDs.
POLL_ALLOWED_CHANNELS = ["polls"]

#emojis dict. May be possible to change incomprehensible unicode to other strings recognized by discord
EMOJIS = {
	"thumbsup": "\U0001f44d",
	"thumbsdown": "\U0001f44e",
	"shrug": "\U0001f937",
}

ADMIN_ROLE = ["Server Admin", "Bot Admin"]
GESTION_ROLES = ["Community Manager", "Server Admin"]
DEV_ROLES = ["Dev"]
for role in ADMIN_ROLE:
	GESTION_ROLES.append(role)
	DEV_ROLES.append(role)

SLAPPED_LOG_FILE = "slapped.txt"
TODO_FILE = "todo.txt"

#INITS THE BOT
bot = commands.Bot(command_prefix=PREFIX)


#########################################
#										#
#										#
#				Checks					#
#										#
#										#
#########################################

def is_author():
	def check_condition(ctx):
		return ctx.message.author.id ==AUTHOR_ID
	return commands.check(check_condition)

def in_channel():
	"""work in progress"""
	def check_condition(ctx):
		return ctx.channel.name == "polls"
	return commands.check(check_condition)

def not_poll():
	def check_condition(ctx):
		return ctx.channel.name not in POLL_ALLOWED_CHANNELS
	return commands.check(check_condition)


#########################################
#										#
#										#
#				Cogs					#
#										#
#										#
#########################################


class BotEssentials(commands.Cog):
	"""All of the essential methods all of our bots should have"""
	def __init__(self, bot):
		self.bot = bot
			
	@commands.Cog.listener()
	async def on_ready(self):
		print('We have logged in as {0.user}'.format(self.bot))

	@commands.Cog.listener()
	async def on_member_join(self, member):

		faq_channel = discord.utils.get(member.guild.channels, name="faq")
		rules_channel = discord.utils.get(member.guild.channels, name="rules")
		await member.guild.system_channel.send("Welcome to {} {}! Please make sure to take a look at our {} and before asking a question, at the {}".format(member.guild.name, member.mention, rules_channel.mention, faq_channel.mention))


	@commands.command()
	async def ping(self, ctx):
		'''This command responds with the current latency.'''
		latency = self.bot.latency
		await ctx.send("**Pong !** Latency of {0:.3f} seconds".format(latency))


	#Command that shuts down the bot
	@commands.command()
	@is_author()
	async def shutdown(self, ctx):
		print("Goodbye")
		await self.bot.change_presence(status=discord.Status.offline)
		#time.sleep(0.1)
		await ctx.send("Goodbye")
		await self.bot.close()
		await quit()



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


class Slapping(commands.Cog):
	"""a suite of commands meant to help moderators handle the server"""
	def __init__(self, bot):
		self.bot = bot
		
	@commands.command()
	@commands.has_any_role(*GESTION_ROLES)
	async def slap(self, ctx, member:discord.Member):
		'''Meant to give a warning to misbehavioring members. Cumulated slaps will result in warnings, role removal and eventually kick. Beware the slaps are loged throughout history and are cross-server'''
		to_write = ""
		slap_count=0

		#reads the file and prepares logging of slaps
		with open(SLAPPED_LOG_FILE, "r") as file:
			content = file.readlines()
			for line in content:
				if line.startswith(str(member.id)):
					slap_count = int(line.split(";")[1])+1
					to_write+= "{};{}\n".format(member.id, slap_count)

				else:
					to_write += line

		#creates a log for the member if he's never been slapped
		if slap_count==0:
			slap_count = 1
			to_write += "{};{}\n".format(member.id, slap_count)


		await ctx.send("{} you've been slapped by {} because of your behavior! This is the {} time. Be careful, if you get slapped too much there *will* be consequences !".format(member.mention, ctx.message.author.mention, slap_count))

		#writes out updated data to the file
		with open(SLAPPED_LOG_FILE, "w") as file:
			file.write(to_write)			

	@commands.command()
	@commands.has_any_role(*GESTION_ROLES)
	async def pardon(self, ctx, member:discord.Member):
		'''Pardonning a member resets his slaps count.'''
		to_write = ""

		#reads the file and prepares logging of slaps
		with open(SLAPPED_LOG_FILE, "r") as file:
			content = file.readlines()
			for line in content:
				if not line.startswith(str(member.id)):
					to_write+=line

		#writting updated file
		with open(SLAPPED_LOG_FILE, "w") as file:
			file.write(to_write)

		await ctx.send("{} you've been pardonned by {}.".format(member.mention, ctx.author.mention))


class Embedding(commands.Cog):
	"""A sutie of command providing users with embeds manipulation tools."""
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


#########################################
#										#
#										#
#			Setup & Execution			#
#										#
#										#
#########################################


bot.add_cog(Role(bot))
bot.add_cog(Slapping(bot))
bot.add_cog(Embedding(bot))
bot.add_cog(Poll(bot))
bot.add_cog(BotEssentials(bot))


bot.run(TOKEN)