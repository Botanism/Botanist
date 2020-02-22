import os
import logging
import discord
import io
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

name = __name__.split(".")[-1]


class PollConfigEntry(ConfigEntry):
    """docstring for PollConfigEntry"""

    def __init__(self, bot, cfg_chan_id):
        super().__init__(bot, cfg_chan_id)
        print("I'm here")

    async def run(self, ctx):
        try:
            tr = Translator(name, get_lang(ctx))
            await self.config_channel.send(tr["start_conf"])
            pursue = await self.get_yn(ctx, tr["pursue"])
            if not pursue:
                return False
            retry = True

            while retry:
                # getting the list of channels to be marked as polls
                poll_channels = await self.get_answer(
                    ctx,
                    tr["poll_channels"].format(self.config_channel.mention),
                    filters=["channels"],
                )
                if self.config_channel in poll_channels:
                    await self.config_channel.send(tr["invalid_chan"])
                    continue

                poll_channels_str = ""
                for chan in poll_channels:
                    poll_channels_str += f"{chan.mention},"
                poll_channels_str = poll_channels_str[:-1]

                confirmed = await self.get_yn(
                    ctx, tr["confirmed"].format(poll_channels_str)
                )
                if not confirmed:
                    # making sure the user really wants to quit
                    drop = await self.get_yn(ctx, tr["drop"])
                    if drop:
                        local_logger.info(
                            f"Poll configuration has been cancelled for server {ctx.guild.name}"
                        )
                        retry = False
                else:
                    retry = False

            poll_channels_ids = []
            for chan in poll_channels:
                poll_channels_ids.append(chan.id)

            with ConfigFile(ctx.guild.id) as conf:
                conf["poll_channels"] = poll_channels_ids

            await self.config_channel.send(tr["conf_done"])
            local_logger.info(
                f"Configuration of poll for server {ctx.guild.name} ({ctx.guild.id}) has been completed."
            )
        except Exception as e:
            raise e


class Poll(commands.Cog):
    """A suite of commands providing users with tools to more easilly get the community's opinion on an idea"""

    def __init__(self, bot):
        self.bot = bot
        self.config_entry = PollConfigEntry

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """currently makes this checks for ALL channels. Might want to change the behavior to allow reactions on other msgs"""

        # fetching concerned message and the user who added the reaction
        message = await self.bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id
        )
        user = self.bot.get_user(payload.user_id)

        # getting poll_allowed_chans
        # @is_init
        with ConfigFile(payload.guild_id) as conf:
            poll_allowed_chans = conf["poll_channels"]

        # checking that user isn't the bot
        if (payload.user_id != self.bot.user.id) and (
            payload.channel_id in poll_allowed_chans
        ):

            # checking wether the reaction should delete the poll
            if payload.emoji.name == EMOJIS["x"]:
                if payload.user.name == message.embeds[0].title:
                    return message.delete()
                else:
                    return reaction.remove(user)

            # checking if reaction is allowed
            elif payload.emoji.name not in [
                EMOJIS["thumbsdown"],
                EMOJIS["thumbsup"],
                EMOJIS["shrug"],
            ]:
                # deleting  reaction of the user. Preserves other reactions
                try:
                    # iterating over message's reactions to find out which was added
                    for reaction in message.reactions:
                        # testing if current emoji is the one just added
                        if reaction.emoji == payload.emoji.name:
                            # removing unauthorized emoji
                            await reaction.remove(user)

                except Exception as e:
                    local_logger.exception(
                        "Couldn't remove reaction {}".format("reaction")
                    )
                    raise e

            # if the reaction is allowed -> recalculating reactions ratio and changing embed's color accordingly
            else:
                # preventing users from having multiple reactions
                for reaction in message.reactions:
                    if reaction.emoji != payload.emoji.name:
                        await reaction.remove(user)

                # currently using integers -> may need to change to their values by checcking them one by one
                react_for = message.reactions[0].count
                react_against = message.reactions[2].count
                # changing color of the embed
                await self.balance_poll_color(
                    message, message.reactions[0].count, message.reactions[2].count
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        # getting poll_allowed_chans
        with ConfigFile(payload.guild_id) as conf:
            poll_allowed_chans = conf["poll_channels"]

        # fetching concerned message and the user who added the reaction
        message = await self.bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id
        )

        # checking that user isn't the bot
        if (payload.user_id != self.bot.user.id) and (
            payload.channel_id in poll_allowed_chans
        ):
            # changing color of the embed
            await self.balance_poll_color(
                message, message.reactions[0].count, message.reactions[2].count
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if not was_init(message):
            await message.channel.send(embed=get_embed_err(ERR_NOT_SETUP))
            return

        # getting poll_allowed_chans
        # poll_allowed_chans = ConfigFile(message.guild.id)["poll_channels"]
        with ConfigFile(message.guild.id) as conf:
            poll_allowed_chans = conf["poll_channels"]

        if (
            message.channel.id in poll_allowed_chans
            and message.content.startswith(PREFIX) != True
        ):

            # rebuilding attachements
            files = []
            for attachment in message.attachments:
                content = await attachment.read()
                io_content = io.BytesIO(content)
                file = discord.File(io_content, filename=attachment.filename)
                files.append(file)

            mentions = message.mentions
            roles = message.role_mentions
            final = message.content
            for men in mentions:
                final = final.replace("<@" + str(men.id) + ">", men.name)

            for role in roles:
                final = final.replace("<@" + str(role.id) + ">", role.name)

            # making embed
            embed_poll = discord.Embed(
                title=message.author.name,
                description=final,
                colour=discord.Color(16776960),
                url=None,
            )
            # embed_poll.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            embed_poll.set_thumbnail(url=message.author.avatar_url)
            # embed_poll.set_footer(text=message.author.name, icon_url=message.author.avatar_url)

            # sending message & adding reactions
            try:
                await message.delete()
                sent_msg = await message.channel.send(embed=embed_poll, files=files)
                await sent_msg.add_reaction(EMOJIS["thumbsup"])
                await sent_msg.add_reaction(EMOJIS["shrug"])
                await sent_msg.add_reaction(EMOJIS["thumbsdown"])

            except Exception as e:
                local_logger.exception("Couldn't send and delete all reaction")

    async def balance_poll_color(self, msg, for_count, against_count):
        r = g = 128
        diff = for_count - against_count
        votes = for_count + against_count
        r -= (diff / votes) * 64
        g += (diff / votes) * 64

        # checking whether the number is over 255
        r = int(min(255, r))
        g = int(min(255, g))

        color = int((r * 65536) + (g * 256))
        # getting messages's embed (there should only be one)
        embed = msg.embeds[0].copy()
        embed.color = color
        await msg.edit(embed=embed)

        return msg

    @commands.group()
    async def poll(self, ctx):
        """a suite of commands that lets one have more control over polls"""
        if ctx.invoked_subcommand == None:
            local_logger.warning("User didn't provide any subcommand")
            raise discord.ext.commands.MissingRequiredArgument(
                "Group requires a subcommand"
            )

    @poll.command()
    async def rm(self, ctx, msg_id):
        """allows one to delete one of their poll by issuing its id"""
        for chan in ctx.guild.text_channels:
            try:
                msg = await chan.fetch_message(msg_id)
                break

            # if the message isn't in this channel
            except discord.NotFound as e:
                local_logger.info("poll isn't in {0.name}[{0.id}]".format(chan))

            except Exception as e:
                local_logger.exception("An unexpected error occured")
                raise e

        # making sure that the message is a poll. doesn't work, any msg with a embed could be considered a poll
        if len(msg.embeds) != 1:
            return
        # checking if the poll was created by the user. Is name safe enough ?
        if msg.embeds[0].title == ctx.author.name:
            try:
                await msg.delete()
            except Exception as e:
                local_logger.exception("Couldn't delete poll".format(msg))
                raise e

    @poll.command()
    async def status(self, ctx, msg_id: discord.Message):
        """returns stats about your running polls. This is also called when one of you poll gets deleted."""
        pass


def setup(bot):
    bot.add_cog(Poll(bot))
