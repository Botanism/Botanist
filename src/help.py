import logging
from asyncio.exceptions import TimeoutError
from asyncio import sleep as asleep
from time import time
import discord
from settings import EMOJIS, HELP_TIME
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

    def __init__(self, react_time: int = HELP_TIME, **options):
        super().__init__(**options)
        self.react_time = react_time

    def help_reaction(self, reaction, user):
        if reaction.emoji not in (
            EMOJIS["arrow_backward"],
            EMOJIS["arrow_forward"],
            EMOJIS["information_source"],
        ):
            return False

        # making sure the author of the help command is indeed the one reacting
        if user == reaction.message.author:
            return False

        return True

    def get_help_lang(self):
        with ConfigFile(self.get_destination().guild.id) as conf:
            lang = conf["lang"]
        return lang

    async def send_bot_help(self, mapping):
        print("in send_bot_help")

    async def send_cog_help(self, cog):
        pass

    async def send_group_help(self, group):
        pass

    async def send_command_help(self, command):
        pages = get_command_pages(command, self.get_help_lang())
        current_page = 0
        msg = await self.get_destination().send(embed=pages[current_page])

        # adding approriate interactions
        if len(pages) > 1:
            await msg.add_reaction(EMOJIS["arrow_backward"])
            await msg.add_reaction(EMOJIS["information_source"])
            await msg.add_reaction(EMOJIS["arrow_forward"])
        else:
            await msg.add_reaction(EMOJIS["information_source"])

        start_time = time()
        elapsed_time = 0
        try:
            while elapsed_time < self.react_time:
                print("waiting for a reaction")
                reaction, user = await self.context.bot.wait_for(
                    "reaction_add",
                    timeout=self.react_time - elapsed_time,
                    check=self.help_reaction,
                )
                print(f"Got reaction {reaction} from {user}")

                # interpret reactions
                if reaction.emoji == EMOJIS["arrow_forward"]:
                    # making sure you're not on the last page
                    local_logger.info("Going forward in paging")
                    if current_page != len(pages) - 1:
                        current_page += 1

                elif reaction.emoji == EMOJIS["arrow_backward"]:
                    local_logger.info("Going backward in paging")
                    # making sure you're not on the first page
                    if current_page != 0:
                        current_page -= 1

                else:
                    # the only other allowed reaction is information_source
                    local_logger.info(
                        "Deleting help embed and sending help interface manual."
                    )
                    await self.send_bot_help(self.get_bot_mapping())
                    await msg.delete()
                    break

                await msg.remove_reaction(reaction, user)
                await msg.edit(suppress=True, embed=pages[current_page])
                elapsed_time = time() - start_time
                # print("Seconds gone by:", elapsed_time)
        except TimeoutError:
            # print("Time is over, deleting message")
            await msg.delete()


def get_help(command: discord.ext.commands.command, lang: str):
    if command.cog:
        text = Translator(command.cog.__module__.split(".")[1], lang, help_type=True)._dict
        if not command.parents:
            return text[command.name]
        else:
            for parent in command.parents:
                text = text[parent.name][1]
            return text[command.name]

    else:
        # the only commands not in a cog are in main.py -> ext group
        return Translator("default", lang, help_type=True)[command.name]


def get_command_pages(
    command: discord.ext.commands.command, lang: str, threshold: int = 150
) -> list:
    """this returns a list of Embeds that represent help pages
    cmd_type is an int that must be 0 (command), 1 (cog), 2 (group)
    maybe return a generator instead?"""
    name = ""
    if command.parents:
        for parent in command.parents:
            name += f"{parent.name} / "
    name += command.name

    description, usage = get_help(command, lang)

    # split command in multiple pages
    if (
        count_chars(description, usage, name) > 2048 - threshold
    ):  # maximum embed description size is 2048 chars
        pages = []
        # splitting by line breaks
        paragraphs = description.split("\n")

        # splitting by "."
        for paragraph in paragraphs:
            if count_chars(paragraph) > 2048 - threshold:
                sentences = paragraph.split(".")
                assert len(sentences) > 0, ValueError(
                    "No known parsing method for this help string. Should contain at least one dot."
                )
                while sentences:
                    page = ""  # the page we're starting to build
                    crt_count = 2048  # how many chars are left before we need to make a new page
                    while (crt_count > threshold) and len(sentences) != 0:
                        # print(sentences)
                        sentence = sentences.pop(0)
                        crt_count -= count_chars(sentence)
                        # /!\ currently not handling the case of sentences larger than 2048 chars
                        assert crt_count > 0, ValueError(
                            "This sentence is over 2048 characters long!"
                        )  # > and not >= because we need to add the dot again
                        page += sentence + "."
                    pages.append(page)

            else:
                pages.append(paragraph)
    else:
        pages = [description]

    # building the embeds from the paged descriptions
    embeds = []
    pages_number = len(pages)
    for page, crt in zip(pages, range(len(pages))):
        embed = discord.Embed(title=name, description=page, color=7506394,)
        embed.set_footer(text=f"Page ({crt+1}/{pages_number})")
        embed.add_field(name="Usage", value=f"{command.name} `{usage}", inline=False)
        embeds.append(embed)

    print(embeds)
    return embeds


def get_command_help(command: discord.ext.commands.command):
    cog_strings = Translator(command.cog.qualified_name, "en", help_type=True)._dict
    if command.parents:
        for parent in command.parents:
            cog_strings = cog_strings[parent]

    return cog_strings[command.name]


def count_chars(*args: str) -> int:
    count = 0
    for string in args:
        assert type(string) == str, TypeError(
            f"args should be of type str not {type(string)}"
        )
        count += len(string)
    return count


def get_commands_tree(command, cmd_type: int = 1) -> dict:
    """returns a dict with a list of all commands strings (reads the JSONs)
    cmd_type can be 1 or 2"""
    assert cmd_type in [1, 2], RuntimeError(f"Invalid value {cmd_type} for cmd_type.")
