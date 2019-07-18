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

    @ext.command()
    async def ls(ctx):
        try:
            enabled= []
            running = []
            disabled = []
            #fetching list of enbaled and disabled extensions
            with ConfigFile(EXTENSIONS_FILE, folder=".") as exts:
                for e in exts:
                    if d[e]==True:
                        enabled.append(e)
                    else:
                        disabled.append(e)

            #checking whether all enabled extensions are running
            for e in bot.extensions.keys():
                running.append(e)

            #building strings
            disabled_str=""
            for e in disabled:
                disabled_str+=f"{EMOJIS["white_circle"]} {e}\n"

            enbaled_str=""
            for e in enabled:
                if e in running:
                    enbaled_str+=f"{EMOJIS["large_blue_circle"]} {e}\n"
                else:
                    enbaled_str+=f"{EMOJIS["red_circle"]} {e}\n"


            #building embed
            ext_embed = discord.Embed(
                title = "Extensions",
                description = "The list of all extensions and their status",
                colour = 7506394,
                url=None)

            ext_embed.set_thumbnail(url=self.bot.avatar_url)
            ext_embed.add_field(name="Enabled", value=enbaled_str, inline=False)
            ext_embed.add_field(name="Disabled", value=disabled_str, inline=False)

            await ctx.send(embed=ext_embed)


        except Exception as e:
            local_logger.exception(e)



def setup(bot):
    bot.add_cog(Development(bot))