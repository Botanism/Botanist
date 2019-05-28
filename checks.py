import logging
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