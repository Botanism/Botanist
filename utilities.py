import logging
import os
import json
from settings import *
from discord.ext import commands


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
local_logger.info(f"Innitalized {__name__} logger")


#########################################
#										#
#										#
#				Checks					#
#										#
#										#
#########################################

def is_runner():
	def check_condition(ctx):
		return ctx.message.author.id ==RUNNER_ID
	result = commands.check(check_condition)
	if result == False:
		pass
		#ctx.send(ERR_UNSUFFICIENT_PRIVILEGE)
	return result

def is_init():
	def check_condition(ctx):
		conf_files = os.listdir()
		file_name = f"{ctx.guild.id}.json"
		#ctx.send(ERR_NOT_SETUP)
		return file_name in conf_files

	return commands.check(check_condition)

def was_init(ctx):
	'''same as the previous function except this one isn't a decorator. Mainly used for listenners'''
	if f"{ctx.guild.id}.json" in os.listdir():
		return True
	return False

def has_auth(clearance, *args):
	def predicate(ctx):
		allowed_roles = get_roles(ctx.guild.id, clearance)
		for role in ctx.author.roles:
			if role.id in allowed_roles:
				return True
		local_logger.send(ERR_UNSUFFICIENT_PRIVILEGE)
		local_logger.warning(ERR_UNSUFFICIENT_PRIVILEGE)
		return False

	return commands.check(predicate)

def is_server_owner():
	def predicate(ctx):
		if ctx.author == ctx.guild.owner:
			return True
		#ctx.send(ERR_UNSUFFICIENT_PRIVILEGE)
		return False

	return commands.check(predicate)


#########################################
#										#
#										#
#			Utility functions			#
#										#
#										#
#########################################

def get_m_time(file):
	return os.getmtime(file+"json")

def has_changed(server, last_time):
	last_update = get_m_time(file)
	if last_update != last_time:
		return True
	return False

def get_conf(guild_id):
	with open(f"{guild_id}.json", "r") as file:
		conf = json.load(file)
	print(conf)
	return conf

def update_conf(guild_id, conf_dict):
	try:
		with open(f"{guild_id}.json", "w") as file:
			json.dump(conf_dict, file)
		return True

	except Exception as e:
		local_logger.exception(e)
		return False

def del_conf(guild_id):
	try:
		os.remove(f"{guild_id}.json")
		return True

	except Exception as e:
		local_logger.exception(e)
		return False

def get_roles(guild_id, lvl):
	try:
		with open(f"{guild_id}.json", "r") as file:
			return json.load(file)["roles"][lvl]

	except Exception as e:
		local_logger.exception(e)
		raise e

def get_poll_chans(guild_id):
	with open(f"{guild_id}.json", "r") as file:
		fl = json.load(file)
		
	chans = fl["poll_channels"]
	if len(chans)==0:
		return None

	return chans
