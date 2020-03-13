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

async def get_event_view(user_id):
    with ConfigFile(str(user_id + ".json"), folder=EVENT_FOLDER) as user_events:
        return user_events.keys()

async def events_from_file(bot, user_id):
    events = []
    with ConfigFile(str(user_id + ".json"), folder=EVENT_FOLDER) as user_events:
        for name, params in user_events.items():
            events.append(Event.from_dict(bot, user_id, name, params))
    return events


class Event(object):
    """This is a data strcuture representing a discord user event."""

    def __init__(
        self,
        bot,
        user_id: int,
        name: str,
        time: int,
        reminder: int = 0,
        description: str = None,
        guild: int = None,
        channel: int = None,
        role: int = None,
    ):
        self.bot = bot
        self.user_id = user_id
        self.name = name
        self.time = time
        self.reminder = reminder
        self.description = description

        if channel:
            self.channel = bot.get_channel(channel)
        else:
            self.channel = None

        if guild:
            self.guild = bot.get_guild(guild)
            if role:
                self.role = self.guild.get_role(role)
            else:
                self.role = None
        else:
            self.guild = None
            self.role = None

    @classmethod
    def from_dict(cls, bot, user_id: int, name: str, params: dict):
        time = params.pop("time")
        return cls(bot, user_id, name, time, **params)

    def save(self):
        pass

    def load(self):
        pass

    async def countdown(self):
        pass


class Time(commands.Cog):
    """A cog which handles reminder events and commands"""

    def __init__(self, bot):
        self.config_entry = None
        self.bot = bot

    @commands.command()
    async def remind(self, ctx, *args):
        """for more information on how argument parsing is done see to_datetime"""
        args = list(args)
        args.append("null") #so that a missing message is detected in the while loop
        print(args)
        delay = 0
        time_factor = to_datetime(args[0], sub=False, lenient=True)

        while time_factor:
            delay += time_factor.total_seconds()
            args.pop(0)
            time_factor = to_datetime(args[0], sub=False, lenient=True)

        # making sure the reminder is not set to current time
        if delay == 0 or len(args) == 1:
            await ctx.send(embed=get_embed_err(ERR_NOT_ENOUGH_ARG))
            return

        # making the text
        text = ""
        for word in args:
            text += f" {word}"

        await asyncio.sleep(delay)
        await ctx.author.send(text)

    @commands.group()
    async def event(self, ctx):
        """event interface with the user.
        Handles creation, tracking and publishing"""
        pass


    @event.command()
    @
    async def new(self, ctx, name: str):
        #making sure an event with the same name isn't already registered for this user
        evts_names = await get_event_view(ctx.author.name)

        await ctx.send(f"Starting creation of {name} event.")


def setup(bot):
    bot.add_cog(Time(bot))
