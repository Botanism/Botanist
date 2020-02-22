import logging
from time import time
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

    def __init__(self, react_time: int = 180, **options):
        super().__init__(**options)

    def help_reaction(self, reaction, user):
        if reaction not in (EMOJIS["arrow_backward"], EMOJIS["arrow_forward"], EMOJIS["information_source"]):
            return False

        if not user == ctx.author:
            return False

        return True


    async def send_bot_help(self, mapping):
        pass

    async def send_cog_help(self, cog):
        pass

    async def send_group_help(self, group):
        pass

    async def send_command_help(self, command):
        pages = get_command_pages(command)
        current_page = 0
        msg = await self.get_destination().send(embed=pages[current_page])

        #adding approriate interactions
        await msg.add_reaction(EMOJIS["information_source"])
        if len(pages)>1:
            #only adding forward since you can't go before the first page!
            await msg.add_reaction(EMOJIS["arrow_forward"])

        start_time = time()
        elapsed_time = 0
        while elapsed_time < self.react_time:
            reaction, user = self.context.bot.wait_for("reaction_add", timeout=self.react_time - elapsed_time, check=self.help_reaction)

            #interpret reactions
            if reaction == EMOJIS["arrow_forward"]:
                #making sure you're not on the last page
                if current_page != len(pages) - 1:
                    current_page += 1
                else:
                    await msg.remove_reaction(reaction, user)

            elif reaction == EMOJIS["arrow_backward"]:
                #making sure you're not on the first page
                if current_page != 0:
                    current_page -= 1
                else:
                    await msg.remove_reaction(reaction, user)

            else:
                #the only other allowed reaction is information_source
                await self.send_bot_help(self.get_bot_mapping())
                await msg.delete()
                break

            await msg.edit(suppress=True, embeds=pages[current_page])
            elapsed_time = time() - start_time
        await msg.delete()


def get_command_pages(command: discord.ext.commands.command, threshold: int = 150) -> list:
    """this returns a list of Embeds that represent help pages
    cmd_type is an int that must be 0 (command), 1 (cog), 2 (group)
    maybe return a generator instead?"""
    name = ""
    if command.parents:
        for parent in command.parents:
            name += f"{parent.name} / "
    name += command.name

    description, usage = get_help(command)

    char_count += count_chars(description, usage, name)
    if char_count > 6000 - threshold:
        #split command in multiple pages
        pass

    embed = discord.Embed(
        title = name,
        description = description,
        usage = f"`{command.name}" + usage,
        color = 7506394)

    return [embed]


def get_command_help(command: discord.ext.commands.command):
    cog_strings = Translator(command.cog.qualified_name, "en", help_type=True)._dict
    if command.parents:
        for parent in command.parents:
            cog_strings = cog_strings[parent]

    return cog_strings[command.name]

def count_chars(*args: str) -> int:
    count = 0
    for string in args:
        assert type(string) == str, TypeError(f"args should be of type str not {type(string)}")
        count += len(string)
    return count


def get_commands_tree(command, cmd_type: int = 1) -> dict:
    """returns a dict with a list of all commands strings (reads the JSONs)
    cmd_type can be 1 or 2"""
    assert cmd_type in [1,2], RuntimeError(f"Invalid value {cmd_type} for cmd_type.")


