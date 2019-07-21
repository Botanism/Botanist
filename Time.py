import discord
import json
import logging
import asyncio
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

class Reminder(commands.Cog):
    """A cog which handles reminder events and commands"""
    def __init__(self, bot):
        self.bot = bot
        self.tf = {
        "d": 86400,
        "h": 3600,
        "m": 60,
        "s": 1
        }
        
    @commands.command()
    async def remind(self, ctx, *args):
        '''the date format is as such:
        d => days
        h => hours
        m => minutes
        s => seconds
        Also the order is important. The time parser will stop once it's reached seconds.'''
        delay = 0
        done = False
        text = ""
        for a in args:
            if not done:
                #parsing the time
                if a[-1] in self.tf.keys():
                    try:
                        delay+=int(a[:-1])*self.tf[a[-1]]
                        if a[-1]=="s": done=True
                    
                    except ValueError as e:
                        #if seconds isn't precised but that the timestamp is done
                        done=True
            else:
                #making the text
                text+=f" {a}"

        if delay==0:
            ctx.send(ERR_NOT_ENOUGH_ARG)
            return

        await asyncio.sleep(delay)
        await ctx.author.send(text)        

def setup(bot):
    bot.add_cog(Reminder(bot))