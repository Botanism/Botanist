import discord
import json
import logging
import asyncio
from time import time as sec_time
from time import gmtime, asctime
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


class Event(object):
    """This is a data strcuture representing a discord user event."""

    empty_event = {"partial": {}, "sent": {}}

    def __init__(
        self,
        bot,
        user_id: int,
        name: str,
        start: int,
        reminder: int = 0,
        description: str = None,
        guild: int = None,
        channel: int = None,
        role: int = None,
        color: discord.Color = 7506394,
        subscribers: list = []
    ):
        self.bot = bot
        self.user_id = user_id
        self.name = name
        self.start = start
        self.reminder = reminder
        self.description = description
        self.color = color
        self.subscribers = subscribers

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

        print("We finished making ", self)
        print(self.load())

    def __repr__(self):
        return f"<exts.time.Event name={self.name}, time={self.start}, reminder={self.reminder}, role={self.role}, channel={self.channel}, guild={self.guild}>"

    @classmethod
    def from_dict(cls, bot, user_id: int, name: str, params: dict):
        print("\nFull dict: ", params)
        start = params.pop("start")
        print("Here are the parameters", params)
        return cls(bot, user_id, name, start, **params)

    def to_dict(self):
        return {
            "start": self.start,
            "reminder": self.reminder,
            "description": self.description,
            "channel": self.channel,
            "guild": self.guild,
            "role": self.role,
            "color": self.color,
            "subscribers": self.subscribers
        }

    def embed(self):
        dates = f"""This message is set to start at **{asctime(gmtime(self.start))}** and participants will be reminded **{asctime(gmtime(self.reminder))}** before the event."""
        preview = discord.Embed(title=self.name, description=dates, color=self.color)
        preview.add_field(name="Description", value=self.description, inline=False)
        if self.guild:
            # the message was sent
            guild_spec = ""
            if self.role:
                guild_spec += (
                    f"The associated role for this event is {self.role.mention}.\n"
                )
            if self.channel:
                guild_spec += f"Discussion takes place in {self.channel.mention}"
            if len(guild_spec):
                preview.add_field(name="Information", value=guild_spec, inline=False)
        return preview

    def save(self):
        tmp_dict = self.to_dict()
        print("\nNormal dict", tmp_dict)
        tmp_dict["color"] = self.color.value
        print("\nThis is the tempdict", tmp_dict)
        with ConfigFile(
            self.user_id, folder=EVENT_FOLDER, default=Event.empty_event
        ) as file:
            file["partial"][self.name] = tmp_dict

    def load(self):
        with ConfigFile(self.user_id, folder=EVENT_FOLDER, default=Event.empty_event) as file:
            if not self.guild:
                return file["partial"][self.name]
            else:
                return file["sent"][self.name]

    async def countdown(self):
        pass


def get_event_view(user_id):
    with ConfigFile(
        str(user_id), folder=EVENT_FOLDER, default=Event.empty_event
    ) as file:
        return list(file["partial"].keys()) + list(file["sent"].keys())


def get_events(user_id, bot):
    with ConfigFile(
        str(user_id), folder=EVENT_FOLDER, default=Event.empty_event
    ) as file:
        partial = []
        print("this is the file", file)
        print(file["partial"])
        for name, event in file["partial"].items():
            partial.append(Event.from_dict(bot, user_id, name, event))

        sent = []
        for name, event in file["sent"].items():
            partial.append(Event.from_dict(bot, user_id, name, event))

        print("\nNow the file is like this: ", file)

        return partial, sent


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
    @discord.ext.commands.dm_only()
    async def new(self, ctx, name: str):
        """creates a new event and starts the creation interface
        TODO: make sure the rest of the "conversation" tales place exclusively in DM

        this command should be sent in a guild so that the bot can get its ID. The creation process will then take place in the DM."""
        # making sure an event with the same name isn't already registered for this user

        interface = ConfigEntry(self.bot, ctx.channel)

        evts_names = get_event_view(ctx.author.id)
        if name in evts_names:
            await ctx.send(
                "An event with the same name is already registered. Type `::event list` to get a list of registered events or `::help event` to learn how events work."
            )
            return

        await ctx.send(
            f"Starting creation of {name} event. You will need to enter details about the event you have in mind. You can always come back on these by using `::event edit <name>`."
        )

        # description
        description = await interface.get_answer(
            ctx, "Please enter the description of your event."
        )  # no need to check for char count since the user can't send more than 2k chars in a single message
        description = description.content
        await ctx.send(
            "Added the following text as description:\n--- **START** ---\n"
            + description
            + "\n--- **STOP** ---"
        )

        # start date
        # TODO: add support for fixed GMT time input instead?
        start_date = await interface.get_datetime(
            ctx,
            "In how much time should the event start? To learn more on the time format type `::help remind`.",
            later=60,
            seconds=True,
        )
        start_date += sec_time()
        await ctx.send(f"The event is set to start at {asctime(gmtime(start_date))}.")

        # remind date
        remind = await interface.get_datetime(
            ctx,
            "How much time before the event starts should the user be reminded?",
            seconds=True,
        )
        await ctx.send(
            f"The reminder will go off at {asctime(gmtime(start_date - remind))}."
        )

        # attributed role
        role = await interface.get_yn(
            ctx,
            "Should a role be made for this event? You will be able to modify its name and permissions directly from your guild once you send the event.",
        )

        # attributed channel
        chan = await interface.get_yn(
            ctx, "Should there be a new channel attributed and dedicated to the event?"
        )

        # color
        color = await interface.get_color(
            ctx,
            "What color should your event be? This should be either an integer or hexadecimal HTML color value (have it start with a `#`).",
        )

        draft = Event(
            self.bot,
            ctx.author.id,
            name,
            start_date,
            reminder=remind,
            description=description,
            color=color,
        )
        draft.save()
        await ctx.send("This is a preview of your event", embed=draft.embed())

    @event.command(alias=["list", "list_events", "events"])
    @discord.ext.commands.dm_only()
    async def ls(self, ctx):
        print("\n\nIn ls\n")
        partial, sent = get_events(ctx.author.id, ctx.bot)
        print(partial)
        events = discord.Embed(
            title="Your events",
            description="This is an exhaustive list of all of your events.",
            color=7506394,
        )

        # partial
        if len(partial) == 0:
            partial_list = "You have no draft events."
        else:
            partial_list = ""
            for event in partial:
                partial_list += f"**{event.name}** starting in **{asctime(gmtime(event.start - sec_time()))}**\n"
        events.add_field(name="Partial", value=partial_list)

        # sent
        if len(sent) == 0:
            sent_list = "You have no ongoing events"
        else:
            sent_list = ""
            for event in sent:
                sent_list += (
                    f"**{event.name}** started **{asctime(gmtime(event.start))}**\n"
                )
        events.add_field(name="Sent", value=sent_list)

        await ctx.send(embed=events)


def setup(bot):
    bot.add_cog(Time(bot))
