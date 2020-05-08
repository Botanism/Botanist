import logging
import discord
import asyncio
import datetime
import os
from settings import *
from utilities import *

#########################################
# 										#
# 										#
# 			Setting up logging			#
# 										#
# 										#
#########################################
local_logger = logging.getLogger(__name__)
local_logger.setLevel(LOGGING_LEVEL)
local_logger.addHandler(LOGGING_HANDLER)
local_logger.info("Innitalized {} logger".format(__name__))


#########################################
# 										#
# 										#
# 			Making commands				#
# 										#
# 										#
#########################################

name = __name__.split(".")[-1]


class CommunityModerationConfigEntry(ConfigEntry):
    """allows to configure spam and abuse commands"""

    def __init__(self, bot, cfg_chan_id):
        super().__init__(bot, cfg_chan_id)

    async def run(self, ctx):
        tr = Translator(name, get_lang(ctx))
        try:
            await ctx.send(tr["start_conf"])
            pursue = await self.get_yn(ctx, tr["pursue"])
            while pursue:
                await ctx.send(tr["ext_explanation"])

                # spam config
                not_integer = True
                while not_integer:
                    mute_nbr = await self.get_answer(ctx, tr["mute_threshold"])
                    for i in mute_nbr.content:
                        if i not in DIGITS:
                            await ctx.send(
                                tr["assert_number"].format(EMOJIS["warning"])
                            )
                            continue
                    not_integer = False
                    mute_nbr = int(mute_nbr.content)

                # abuse config
                has_chan = False
                while not has_chan:
                    chan = await self.get_answer(
                        ctx, tr["mod_chan"], filters=["channels"]
                    )
                    if len(chan) != 1:
                        ctx.send(tr["exactly_one"])
                        continue
                    has_chan = True

                confirm = await self.get_yn(
                    ctx, tr["confirm_settings"].format(mute_nbr, chan[0].mention)
                )
                if confirm:
                    with ConfigFile(ctx.guild.id) as conf:
                        conf["commode"]["spam"]["mute"] = mute_nbr
                        conf["commode"]["reports_chan"] = chan[0].id
                    pursue = False
                else:
                    retry = await self.get_yn(ctx, tr["retry"])
                    if retry:
                        continue
                    else:
                        pursue = False

        except Exception as e:
            raise e


class Slapping(commands.Cog):
    """a suite of commands meant to help moderators handle the server"""

    def __init__(self, bot):
        self.bot = bot
        self.config_entry = CommunityModerationConfigEntry
        self.spams = {}

    @commands.command(aliases=["warn"])
    @is_init()
    @has_auth("manager")
    async def slap(self, ctx, member: discord.Member, *reason):
        """Meant to give a warning to misbehavioring members. Cumulated slaps will result in warnings, role removal and eventually kick. Beware the slaps are loged throughout history and are cross-server"""
        tr = Translator(name, get_lang(ctx))
        if not len(reason):
            reason = tr["default_reason"]
        else:
            reason_str = ""
            for word in reason:
                reason_str += f" {word}"
            reason = reason_str

        with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
            if member.id in slaps:
                count = len(slaps[str(member.id)]) + 1
            else:
                count = 1

            # warning
            warning = discord.Embed(
                color=16741632, description=tr["slap_description"].format(reason, count)
            )
            warning.set_author(
                name=tr["slap_title"].format(member, ctx.author.name),
                icon_url=member.avatar_url,
            )
            msg = await ctx.send(embed=warning)
            if not member.bot:
                await member.send(
                    tr["slap_dm"].format(ctx.guild.name, ctx.channel.mention),
                    embed=warning,
                )
            await ctx.message.delete()

            # building slap log for `slaps`
            entry = [ctx.author.id, msg.jump_url, reason]
            history = slaps.setdefault(str(member.id), [entry])
            if history != [entry]:
                history.append(entry)

        # making audit to mod chan
        await audit(ctx.guild, embed=warning)

    @commands.command(alias=["pardon"])
    @is_init()
    @has_auth("manager")
    async def forgive(self, ctx, member: discord.Member, nbr=0):
        tr = Translator(name, get_lang(ctx))
        """Pardonning a member to reduce his slap count"""

        with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
            if not str(member.id) in slaps:
                await ctx.send(tr["not_slapped"].format(member))
                return

            s = slaps[str(member.id)]
            if nbr == 0 or len(s) < nbr:
                slaps.pop(str(member.id))
                count = 0
            else:
                for i in range(nbr):
                    slaps[str(member.id)].pop()
                count = len(slaps[str(member.id)])

            # pardon
            slp_nbr = nbr or tr["slp_nbr_all"]
            pardon = discord.Embed(
                description=tr["forgive_description"].format(nbr or "all", count), color=6281471,
            )
            pardon.set_author(
                name=tr["forgive_title"].format(member, ctx.author.name),
                icon_url=member.avatar_url,
            )
            if not member.bot:
                await member.send(
                    tr["slap_dm"].format(ctx.guild.name, ctx.channel.mention),
                    embed=pardon,
                )

        # making audit to mod chan
        await audit(ctx.guild, embed=pardon)

    async def slaps_overview(self, ctx):
        tr = Translator(name, get_lang(ctx))

        with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
            # building slapped members listing
            member_list = ""
            obsolete_entries = []
            for m in slaps:
                member = ctx.guild.get_member(int(m))

                # making sure the user is still a member, if not, delete
                if not member:
                    obsolete_entries.append(m)
                    continue

                member_list += f"\n{member.mention}:\t**{len(slaps[m])}**"

            for entry in obsolete_entries:
                slaps.pop(entry)

            # checking if there's any slap
            if len(slaps) == 0:
                await ctx.send(tr["no_slaps"] + EMOJIS["tada"])
                return

        # if a user has been slapped
        embed = discord.Embed(
            title=tr["slaps_title"] + EMOJIS["hammer"],
            description=tr["slaps_description"],
            colour=16741632,
        )  # used to be blurpple 7506394

        embed.add_field(name=tr["member_list"], value=member_list)
        return embed

    def get_member_slaps(self, ctx, member):
        tr = Translator(name, get_lang(ctx))
        with ConfigFile(ctx.guild.id, folder=SLAPPING_FOLDER) as slaps:
            if str(member.id) not in slaps:
                return tr["not_slap_hist"]

            slaps_list = ""
            for slap in slaps[str(member.id)]:
                slaps_list += tr["crt_str"].format(
                    slap[1], ctx.guild.get_member(slap[0]).mention, slap[2]
                )

        return slaps_list

    @commands.command(aliases=["warnings"])
    @is_init()
    @has_auth("manager")
    async def slaps(self, ctx, *members: discord.Member):
        """returns an embed representing the number of slaps of each member. More detailed info can be obtained if member arguments are provided."""
        tr = Translator(name, get_lang(ctx))

        if len(members) == 0:
            eb = await self.slaps_overview(ctx)
            if eb:
                await ctx.send(embed=eb)
            return

        # only selecting the 10 first members because we can't have more fields
        if len(members) > 10:
            opt_msg = [tr["too_many"].format(len(members))]
        else:
            opt_msg = []

        embed = discord.Embed(
            title=tr["slaps_title"] + EMOJIS["hammer"],
            description=tr["slaps_description"],
            colour=16741632,  # used to be blurple 7506394
        )

        for member in members[:10]:
            embed.add_field(
                name=tr["new_field_name"].format(member),
                value=self.get_member_slaps(ctx, member),
            )

        await ctx.send(*opt_msg, embed=embed)

    async def make_mute(self, channel, member, time):
        seconds = time.total_seconds()

        with ConfigFile(channel.guild.id, folder=TIMES_FOLDER) as count:
            free_at = datetime.datetime.now().timestamp() + seconds
            if str(member.id) in count.keys():
                same = False
                for chan in count[str(member.id)]:
                    if int(chan[0]) == channel.id:
                        chan[1] = int(chan[1]) + seconds
                        same = True

                if not same:
                    count[str(member.id)].append((channel.id, free_at))

            else:
                count[str(member.id)] = [(channel.id, free_at)]

        await channel.set_permissions(
            member, overwrite=discord.PermissionOverwrite(send_messages=False)
        )
        await asyncio.sleep(seconds)
        await channel.set_permissions(
            member, overwrite=discord.PermissionOverwrite(send_messages=None)
        )

    @commands.command()
    @is_init()
    @has_auth("manager")
    async def mute(self, ctx, member: discord.Member, time, whole: bool = False):
        until = to_datetime(time, sub=False)
        if not whole:
            await self.make_mute(ctx.channel, member, until)
        else:
            await ctx.send(COMING_SOON)

    @commands.command()
    @is_init()
    async def spam(self, ctx, member: discord.Member):
        """allows users to report spamming"""
        tr = Translator(name, get_lang(ctx))
        if not ctx.guild in self.spams:
            self.spams[ctx.guild] = {}

        g_spams = self.spams[ctx.guild]

        if member not in g_spams.keys():
            g_spams[member] = [ctx.author]
        else:
            if ctx.author in g_spams[member]:
                await ctx.send(EMOJIS["warning"] + tr["cant_multi_spam"])
            else:
                g_spams[member].append(ctx.author)

                # checking if a threshold was reached
                amount = len(g_spams[member])
                with ConfigFile(ctx.guild.id) as conf:
                    com = conf["commode"]["spam"]
                    # muting user if necessary
                    if amount % com["mute"] == 0:
                        await self.make_mute(
                            ctx.channel, member, datetime.timedelta(seconds=960)
                        )
                        await ctx.send(
                            EMOJIS["zip"] + tr["spam_muted"].format(member.mention)
                        )

        self.spams[ctx.guild] = g_spams

    @commands.command()
    @is_init()
    async def abuse(self, ctx, member: discord.Member, *reason):
        if len(reason) == 0:
            raise discord.ext.commands.MissingRequiredArgument(
                "You need to provide a reason."
            )

        tr = Translator(name, get_lang(ctx))
        with ConfigFile(ctx.guild.id) as conf:
            mod_chan = conf["commode"]["reports_chan"]

        if mod_chan == False:
            await ctx.send(
                "The server owner has disabled this feature because he didn't set any moderation channel. Contact him/her if you think this is not right."
            )
        else:
            mod_chan = ctx.guild.get_channel(mod_chan)

        reason_str = ""
        for word in reason:
            reason_str += f" {word}"

        report = tr["report"].format(
            ctx.author.mention,
            ctx.message.jump_url,
            member.mention,
            ctx.channel.mention,
        )

        card = discord.Embed(
            title=tr["report_title"],
            timestamp=datetime.datetime.now(),
            color=16729127,
            description=report,
        )

        card.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        card.add_field(name=tr["reason_name"], value=reason_str)
        await mod_chan.send(embed=card)


def setup(bot):
    bot.add_cog(Slapping(bot))
