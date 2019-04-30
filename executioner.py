#!/usr/bin/env python3

import discord
from discord.ext import commands
from discord.utils import find as dfind
import math
import requests as rq
from bs4 import BeautifulSoup
import time
import random

#global settings
PREFIX = "::"
TOKEN = "your_token"

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

#inits the bot
bot = commands.Bot(command_prefix=PREFIX)

#Checks
def is_author():
	def check_condition(ctx):
		return ctx.message.author.id ==289426079544901633
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


#events handler
@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	#ctx.send("The Executioner has come...")


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

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

	await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
	'''currently makes this checks for ALL channels. Might want to change the behavior to allow reactions on other msgs'''
	#checking that user isn't the bot
	print(reaction.message.channel.name)
	if user != bot and (reaction.message.channel.name in POLL_ALLOWED_CHANNELS):
		#checking if reaction is allowed
		if reaction.emoji not in [EMOJIS["thumbsdown"],EMOJIS["thumbsup"],EMOJIS["shrug"]]:
			await reaction.remove(user) #deleting  reaction of the user. Preserves other reactions


@bot.event
async def on_member_join(member):
	#welcome_channel = member.guild.system_channel
	faq_channel = discord.utils.get(member.guild.channels, name="faq")
	rules_channel = discord.utils.get(member.guild.channels, name="rules")
	await member.guild.system_channel.send("Welcome to {} {}! Please make sure to take a look at our {} and before asking a question, at the {}".format(member.guild.name, member.mention, rules_channel.mention, faq_channel.mention))	



#bot commands

@bot.command()
async def ping(ctx):
	'''This command responds with the current latency. Also this docstring is automagically turned into the output of the help command'''
	latency = bot.latency #included in the API
	#send replies to the message received. This means in the same channel.
	await ctx.send("Latency of {0:.3f} seconds".format(latency))

@bot.group(pass_context=True)
@commands.has_any_role(GESTION_ROLES)
async def role(ctx):
	'''role management utility. Requires the an Admin role'''
	if ctx.invoked_subcommand is None:
		await ctx.send("Couldn't parse command: Not Enough Arguments")

@role.command(name="add")
async def _add(ctx, role, user):
	'''add role(s) to a user.
	Usage: add role user'''
	#finds the frist matching 
	user = dfind(lambda u: u.name == user, ctx.channel.guild.members)
	role = dfind(lambda r: r.name == role, ctx.channel.guild.roles)
	await user.add_roles(role)

@role.command(name="rm")
async def _rm(ctx, role, user):
	'''removes role(s) to a user
	Usage: rm role user'''
	user = dfind(lambda u: u.name == user, ctx.channel.guild.members)
	role = dfind(lambda r: r.name == role, ctx.channel.guild.roles)
	await user.remove_roles(role)

@bot.command(pass_context=True)
@commands.has_any_role(*GESTION_ROLES)
async def slap(ctx, user):
	'''Meant to give a warning to misbehavioring users. Cumulated slaps will result in warnings, role removal and eventually kick. Beware the slaps are loged throughout history and are cross-server'''
	to_write = ""

	#gets member object
	if type(user)==str:
		if user.startswith("<@"):
			member = dfind(lambda m: m.id == int(user.split(">")[0].split("@")[1]), ctx.guild.members)
		else:
			member = dfind(lambda m: m.name == user, ctx.guild.members)

	else:
		await ctx.send("TypeError: <user> is of an incorrect format")

	if member == None:
		await ctx.send("Couldn't find {} in this server".format(user))
		return

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

	#creates a log for the user if he's never been slapped
	if slap_count==0:
		slap_count = 1
		to_write += "{};{}\n".format(member.id, slap_count)


	await ctx.send("{} you've been slapped by {} because of your behavior! This is the {} time. Be careful, if you get slapped too much there *will* be consequences !".format(member.mention, ctx.message.author.mention, slap_count))

	#writes ou tupdated data to the file
	with open(SLAPPED_LOG_FILE, "w") as file:
		file.write(to_write)


@bot.command(pass_context=True)
@commands.has_any_role(*GESTION_ROLES)
async def pardon(ctx, user):
	'''Pardonning a user resets his slaps count.'''
	to_write = ""

	#gets member object
	if type(user)==str:
		if user.startswith("<@"):
			member = dfind(lambda m: m.id == int(user.split(">")[0].split("@")[1]), ctx.guild.members)
		else:
			member = dfind(lambda m: m.name == user, ctx.guild.members)

	else:
		await ctx.send("TypeError: <user> is of an incorrect format")

	if member == None:
		await ctx.send("Couldn't find {} in this server".format(user))
		return

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

@bot.command(pass_context=True)
async def embed(ctx, *args):
	"""allows you to post a message as an embed. Your msg will be reposted by the bot as an embed !"""
	if ctx.channel.name in POLL_ALLOWED_CHANNELS:
		await ctx.message.delete()
		return

	msg = ""
	for arg in args:
		msg += " {}".format(arg)
	#msg = msg.split(" ")[1:]
	embed_msg = discord.Embed(
			title = None,
			description = msg,
			colour = ctx.author.color,
			url = None
			)

	embed_msg.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)

	await ctx.message.delete()
	await ctx.message.channel.send(embed=embed_msg)

@bot.group(pass_context=True)
async def poll(ctx, question):
	'''does the same as writting in the poll channel. Not yet implemented, I'll have to see if it's of any use at all.'''
	if ctx.invoked_subcommand is None:
		await ctx.send("Couldn't parse command: Not Enough Arguments")

@poll.command(pass_context=True)
async def add(ctx, channel_name):
	'''allows to add a channel to the acepted list of poll channels. Currently only supports channel IDs.'''
	pass

@bot.group(pass_context=True)
async def todo(ctx):
	'''prints out the to-do list with only planned and in the works items. See the reference channel for the full list'''
	if ctx.invoked_subcommand is None:
		#show todo list
		pass

@todo.command(pass_context=True)
@commands.has_any_role(DEV_ROLES)
async def mkdone(ctx, item_id):
	pass

@todo.command(pass_context=True)
@commands.has_any_role(DEV_ROLES)
async def new(ctx, description):
	pass


@bot.command(pass_context=True)
async def clear(ctx, nbr=1, user=None):
	pass



#Command that shuts down the bot
@bot.command()
@is_author()
async def shutdown(ctx):
	print("Goodbye")
	await bot.change_presence(status=discord.Status.offline)
	#time.sleep(0.1)
	await ctx.send("Goodbye")
	await bot.close()
	await quit()




bot.run(TOKEN)