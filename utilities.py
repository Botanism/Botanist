import logging
import os
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
		ctx.send(ERR_UNSUFFICIENT_PRIVILEGE)
	return result

def is_init():
	def check_condition(ctx):
		conf_files = os.listdir()
		file_name = f"{ctx.guild.id}.json"
		return file_name in conf_files

	result = commands.check(check_condition)
	if result == False:
		ctx.send(ERR_NOT_SETUP)
	return result


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
		return conf = json.load(file)

def update_conf(guild_id, conf_dict):
	try:
		with open(f"{guild_id}.json", "r") as file:
			json.dump(file, conf_dict)
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