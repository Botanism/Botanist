import logging
import discord
import asyncio
import os
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

    @commands.Cog.listener()
    async def on_guild_join():
        


    @commands.group()
    @is_server_owner()
    async def cfg(self, ctx):
        self.ad_msg = "I ({}) have recently been added to this server! I hope I'll be useful to you. Hopefully you won't find me too many bugs. However if you do I would appreciate it if you could report them to the [server]({}) where my developers are ~~partying~~ working hard to make me better. This is also the place to share your thoughts on how to improve me. Have a nice day and hopefully, see you there {}".format(ctx.me.mention, DEV_SRV_URL, EMOJIS["wave"])
        if ctx.invoked_subcommand == None:
            await ctx.send(ERR_NO_SUBCOMMAND)

    async def make_cfg_chan(self, ctx):
        overwrite = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.owner : discord.PermissionOverwrite(read_messages=True)
        }
        self.config_channels[ctx.guild.id] = await ctx.guild.create_text_channel("cli-bot-config", overwrites=overwrite)
        return self.config_channels[ctx.guild.id]