from settings import *
from discord.ext import commands


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