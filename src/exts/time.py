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
        args.append("null")  # so that a missing message is detected in the while loop
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
    async def new(self, ctx, name: str):
        """creates a new event and starts the creation interface
        TODO: merge with ConfigEntry class
        TODO: refactor time checkers
        TODO: merge attributions with ConfigEntry methods
        TODO: make sure the rest of the "conversation" tales place exclusively in DM

        this command should be sent in a guild so that the bot can get its ID. The creation process will then take place in the DM."""
        # making sure an event with the same name isn't already registered for this user

        evts_names = await get_event_view(ctx.author.name)
        if name in evts_names:
            await ctx.send(
                "An event with the same name is already registered. Type `::event list` to get a list of registered events or `::help event` to learn how events work."
            )
            return

        await ctx.send(
            f"Starting creation of {name} event. You will need to enter details about the event you have in mind. You can always come back on these by using `::event edit <name>`."
        )

        await ctx.send("Which guild is this event for?")


        # description
        await ctx.send(
            "Please enter the description of your event."
        )  # no need to check for char count since the user can't send more than 2k chars in a single message
        description = await ctx.bot.wait_for("message")
        await ctx.send("Added the following text as description:\n--- **START** ---")
        await ctx.send(description)
        await ctx.send("--- **STOP** ---")

        # start date
        # TODO: add support for fixed GMT time input instead?
        await ctx.send(
            "In how much time should the event start? To learn more on the time format type `::help remind`."
        )
        true_time = False
        while not true_time:
            time = await ctx.bot.wait_for("message")
            true_time = to_datetime(time, lenient=True)

            if true_time == False:
                await ctx.send("The time you entered is incorrect, please try again.")
                continue
            else:
                if true_time.total_seconds() + 30 <= time.time():
                    continue

        start_date = true_time.total_seconds()
        await ctx.send(f"The event is set to start in {true_time}.")

        # remind date
        await ctx.send(
            "How long before the event starts should subscribed users be reminded?"
        )
        true_time = False
        while not true_time:
            time = await ctx.bot.wait_for("message")
            true_time = to_datetime(time, sub=False, lenient=True)

            if true_time == False:
                await ctx.send("The time you entered is incorrect, please try again.")
                continue
        remind = true_time.total_seconds()
        await ctx.send(f"The reminder will go off in {start_date - true_time}.")

        # attributed role
        await ctx.send("Should a role be made for this event?")
        answer = await ctx.bot.wait_for("message", check=ConfigEntry.is_yn_answer)
        if answer:
            role = True
        else:
            role = False

        # attributed channel
        await ctx.send(
            "Should there be a new channel attributed and dedicated to the event?"
        )
        answer = await ctx.bot.wait_for("message", check=ConfigEntry.is_yn_answer)


def setup(bot):
    bot.add_cog(Time(bot))
