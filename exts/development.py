import discord
import json
import logging
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


class Development(commands.Cog):
    """A suite of commands meant to let users give feedback about the bot: whether it's suggestions or bug reports.
    It's also meant to let server owners know when there's an update requiring their attention."""
    def __init__(self, bot):
        self.bot = bot
        self.config_entry = None


    @commands.command()
    @commands.is_owner()
    async def update(self, ctx, *words): #should message be put in settings.py ?
        '''Lets the owner of the bot update the bot from github's repositery. It also sends a notification to all server owners who use the bot. The message sent in the notification is the description of the release on github.
        NB: as of now the bot only sends a generic notification & doesn't update the bot.'''
        #building message
        if len(words)==0:
            message = DEFAULT_UPDATE_MESSAGE
        else:
            message = ""
            for w in words:
                message+=f" {w}"

        owners = []
        for g in self.bot.guilds:
            if g.owner not in owners: owners.append(g.owner)
            
        for o in owners:
            await o.send(message)

    @commands.command()
    @commands.is_owner() #-> this needs to be changed to is_dev()
    async def log(self, ctx):
        '''returns the bot's log as an attachement'''
        #getting the log
        with open(LOG_FILE, "r") as file:
            log = discord.File(file)

        #sending the log
        await ctx.send(file=log)

    @commands.command()
    async def dev(self, ctx):
        """sends the developement server URL to the author of the message"""
        await ctx.author.send("I'm full of joy seeing how interested you seem to be about me! Hopefully it's not for a bug report... In any case, here's the server where I'm developed: " + DEV_SRV_URL)




def setup(bot):
    bot.add_cog(Development(bot))