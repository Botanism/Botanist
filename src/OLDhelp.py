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


class Help(discord.ext.commands.DefaultHelpCommand):
    """docstring for Help. An interactive object that issues help to the servers and DMs."""

    def __init__(self, language, **options):
        super(Help, self).__init__(**options)
        self.lang = language
        self.paginator = Paginator()

    def load_help(self, ext):
        return Translator(ext, self.lang, help_type=True)._dict

    def to_cmds(self, grp):
        cmds = []
        for cmd in grp:
            cmds.append()

    async def send_bot_help(self, mapping):
        strings = self.load_help("help")
        pages = self.paginator.to_embeds(
            "Help Interface", description=strings["description"]
        )
        await self.get_destination().send(embed=pages[0])

    async def send_cog_help(self, cog):
        if isinstance(cog, discord.ext.commands.Cog):
            name = cog.qualified_name.lower()
        else:
            name = "defaults"

        description = self.load_help("help")[name]

        cmds = []
        helps = self.load_help(name)
        for cmd in helps:
            crt = helps[cmd]
            if isinstance(crt[1], dict):
                crt = "` " + crt[0]
            else:
                crt = " " + crt[1]

            cmds.append("`" + cmd + crt)

        pages = self.paginator.to_embeds(
            name.title(), description=description, commands=cmds
        )
        await self.get_destination().send(embed=pages[0])

    async def send_group_help(self, group):
        title = f"**{group.name.title()}**"

        if group.cog:
            title += f" from extension **{group.cog.qualified_name}**"

        if not group.parents:
            description, cmds = self.load_help(group.cog_name.lower())[group.name]

        else:  # this may fail
            path = self.load_help()[
                group.cog.qualified_name.lower()
            ]  # what if it's None for external ones?
            for parent in group.parents:
                path = path[parent.qualified_name]
            description, cmds = path[1][group.name]

        cmds_str = ""
        for cmd in cmds:
            cmds_str += f"--`{cmd}` " + cmds[cmd][0].lower() + "\n"
            # add a list of commands and their description/usage

        embed_help = discord.Embed(title=title, description=description, color=7506394)

        embed_help.add_field(name="Commands", value=cmds_str)
        await self.get_destination().send(embed=embed_help)

    async def send_command_help(self, command):
        title = f"**{command.name.title()}**"

        if command.cog:
            title += f" from extension **{command.cog.qualified_name}**"

        if not command.parents:
            description, usage = self.load_help(command.cog.qualified_name.lower())[
                command.name
            ]
        else:
            path = self.load_help()[command.cog.qualified_name.lower()]
            for parent in command.parents:
                path = path[parent.qualified_name]
            description, usage = path[1][command.name]

        usage = "`" + command.name + " " + usage

        embed_help = discord.Embed(title=title, description=description, color=7506394)

        embed_help.add_field(name="Usage", value=usage)
        await self.get_destination().send(embed=embed_help)


class Paginator:
    """makes the help pages"""

    def __init__(self, base_offset="--", title="Help Interface"):
        self.max_size = 5997
        self._count = 0
        self.base_offset = base_offset
        self._title = title
        self.clear()

    def clear(self):
        self.pages = []
        self._current_page = {"title": self._title, "description": "", "color": 7506394}

    def add_line(self, line="", empty=False, offset=0):
        if self._count + len(line + offset * self.base_offset) > self.max_size:
            raise RuntimeError("Line is too big for the current page.")

        self._current_page["description"] += "\n" + offset * self.base_offset + line
        if empty:
            self._current_page["description"] += "\n"

        self._count -= len(self._current_page)
        if self.chars_left() <= 2:
            self.close_page()

    def chars_left(self, plus=""):
        if not plus:
            return self.max_size - self._count
        else:
            return self.max_size > self._count + len(plus)

    def close_page(self):
        self.pages.append(self._current_page)
        self._count = self._title
        self._current_page = {"title": self._title, "description": "", "color": 7506394}

    def help_page(self, title=None, description="", commands=[]):
        if title == None:
            rtitle = self._title
        else:
            rtitle = str(title)

        embed = {"title": rtitle, "description": description}
        self._count -= len(rtitle + description)
        for line in commands:
            if not self.chars_left(plus=line):
                self.close_page()
            print(line, type(line))
            self.add_line(line=line, empty=True, offset=1)

        self.close_page()
        return embed

    def to_embeds(self, title, description="", commands=[], usage_title="Commands"):
        embed0 = self.help_page(title=title, description=description, commands=commands)
        embeds = [discord.Embed(**embed0, color=7506394)]
        if len(description + title) <= self.max_size and self.pages[0]["description"]:
            embeds[0].add_field(name=usage_title, value=self.pages[0]["description"])

        for page in self.pages[1:]:
            embeds.append(discord.Embed(**page, color=7506394))

        return embeds
