import logging
import os
import json
import discord
from settings import *
from utilities import *

#########################################
#                                       #
#                                       #
#           Setting up logging          #
#                                       #
#                                       #
#########################################
local_logger = logging.getLogger(__name__)
local_logger.setLevel(LOGGING_LEVEL)
local_logger.addHandler(LOGGING_HANDLER)
local_logger.info("Innitalized {} logger".format(__name__))

#########################################
#                                       #
#                                       #
#           Making commands             #
#                                       #
#                                       #
#########################################


class InteractiveHelp(discord.ext.commands.DefaultHelpCommand):
    """This Help class offers interaction support through embeds and reactions."""

    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping):
        pass

    async def send_cog_help(self, cog):
        pass

    async def send_group_help(self, group):
        pass

    async def send_command_help(self, command):
        pass

    async def command_not_found(string):
        pass

    async def subcommand_not_found(command, string):
        pass


def get_pages(command, type: int = 0) -> list:
    """this returns a list of Embeds that represent help pages
    type is and int that must be 0 (command), 1 (cog), 2 (group) """
    pass
