"""Essential features all bot built with this template should have.
Do note that disabling it will cause issues to the config extension."""
import datetime
import logging
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
#               BotEssentials           #
#                                       #
#                                       #
#########################################
'''This cog contains all the basemost functions that all bots should contain.
See https://github.com/s0lst1ce/Botanist for more information'''

class EssentialsConfigEntry(ConfigEntry, metaclass=Singleton):
    """docstring for EssentialsConfigEntry"""
    def __init__(self, bot, cfg_chan_id):
        super().__init__(bot, cfg_chan_id)
        self.msgs = {
        "welcome": ["Do you want to have a welcome message sent when a new user joins the server?",
                    "Enter the message you'd like to be sent to the new users. If you want to mention them use `{0}`"],
        "goodbye": ["Do you want to have a goodbye message sent when an user leaves the server?",
                    "Enter the message you'd like to be sent when an user leaves. If you want to mention them use `{0}`"]
        }


    async def run(self, ctx):
        #welcome & goodbye messages
        try:
            for wg in self.msgs:
                await self.config_channel.send(f"**Starting {wg} message configuration**")
                retry = await self.get_yn(ctx, self.msgs[wg][0])
                message = False

                while retry:

                    message = await self.get_answer(ctx, self.msgs[wg][1])

                    await self.config_channel.send("To make sure the message is as you'd like I'm sending it to you.\n**-- Beginning of message --**")
                    await self.config_channel.send(message.content.format(ctx.guild.owner.mention))
                    response = await self.get_yn(ctx, f"**--End of message --**\nIs this the message you want to set as the {wg} message?")
                    #the user has made a mistake
                    if response == False:
                        response = await self.get_yn(ctx, "Do you want to retry?")
                        if response == False:
                            message = False
                            retry = False
                        #otherwise retry
                        continue

                    else: retry = False

                if message == False: return
                with ConfigFile(ctx.guild.id) as conf:
                    conf["messages"][wg]= message.content

        except Exception as e:
            local_logger.exception(e)
            raise e


class Essentials(commands.Cog):
    """All of the essential methods all of our bots should have"""
    def __init__(self, bot):
        self.bot = bot
        self.config_entry = EssentialsConfigEntry


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """handles command errors"""
        raise error
        local_logger.error(error)
        if type(error) in ERRS_MAPPING.keys():
            await ctx.send(embed=get_embed_err(ERRS_MAPPING[type(error)]))
        else:
            await ctx.send(embed=get_embed_err(ERR_UNEXCPECTED))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open(f"{guild.id}.json", "w") as file:
            json.dump(DEFAULT_SERVER_FILE)
        local_logger.info(f"Joined server {guild.name}")

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as {0.user}'.format(self.bot))
        local_logger.info('Logged in as {0.user}'.format(self.bot))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        local_logger.info("User {0.name}[{0.id}] joined {1.name}[{1.id}]".format(member, member.guild))
        with ConfigFile(member.guild.id) as conf:
            welcome_msg = conf["messages"]["welcome"]
        if welcome_msg != False:
            await member.guild.system_channel.send(welcome_msg.format(member.mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        local_logger.info("User {0.name}[{0.id}] left {1.name}[{1.id}]".format(member, member.guild))
        with ConfigFile(member.guild.id) as conf:
            goodbye_msg = conf["messages"]["goodbye"]
        if goodbye_msg != False:
            await member.guild.system_channel.send(goodbye_msg.format(member.mention))

    @commands.command()
    async def ping(self, ctx):
        '''This command responds with the current latency.'''
        latency = self.bot.latency
        await ctx.send(f"""{EMOJIS["ping_pong"]} Latency of {latency:.3f} seconds""")

    #Command that shuts down the bot
    @commands.command()
    @is_runner()
    async def shutdown(self, ctx):
        print("Goodbye")
        local_logger.info("Switching to invisible mode")
        await self.bot.change_presence(status=discord.Status.offline)
        await ctx.send(f"""Going to sleep {EMOJIS["sleeping"]}""")
        local_logger.info("Closing connection to discord")
        await self.bot.close()
        local_logger.info("Quitting python")
        await quit()

    @commands.command()
    @has_auth("manager")
    async def clear(self, ctx, *filters):
        '''deletes specified <nbr> number of messages in the current channel'''
        #building arguments
        filters = list(filters)
        nbr = None
        period = None
        members = []
        try:
            nbr = int(filters[0])
            filters.pop(0)
        except:
            pass

        if filters:
            period = to_datetime(filters[0])
            if period:
                filters.pop(0)

            for m in filters:
                try:
                    members.append(await discord.ext.commands.MemberConverter().convert(ctx, m))
                except:
                    raise discord.ext.commands.ArgumentParsingError(f"Unrecognized filter {m}")

        hist_args = {}
        if period:
            hist_args["after"] = period
        if nbr and not members:
            hist_args["limit"] = nbr+1
        if not (period or nbr):
            raise discord.ext.commands.ArgumentParsingError("Can't delete all messages of a user!")

        to_del = []
        now = datetime.datetime.now()
        async for msg in ctx.channel.history(**hist_args):
            if not members or msg.author in members:
                local_logger.info("Deleting {}".format(msg))
                if (msg.created_at - now).days <= -14:
                    await msg.delete()
                else:
                    to_del.append(msg)

                if nbr!=None:
                    if nbr <=0:
                        break
                    nbr -= 1

        try:
            await ctx.channel.delete_messages(to_del)

        except discord.HTTPException as e:
            raise e

        except Exception as e:
            local_logger.exception("Couldn't delete at least on of{}".format(to_del))
            raise e

    @commands.command()
    async def status(self, ctx):
        '''returns some statistics about the server and their members'''
        stats = discord.Embed(name="Server Info", description=f"{ctx.guild.name} was created on {str(ctx.guild.created_at)[:10]} and belongs to {ctx.guild.owner.name}. Since then {ctx.guild.member_count-1} users have joined it.", color=7506394)
        stats.set_thumbnail(url=ctx.guild.icon_url)

        #member stats
        mstatus = {"online":0, "idle":0, "dnd":0, "offline":0}
        for member in ctx.guild.members:
            mstatus[str(member.status)] += 1
        #-> change to make use of custom emojis
        status_str = '{online} online\n{idle} idling\n{dnd} not to disturb\n{offline} offline'.format(**mstatus)
        stats.add_field(name=f"Member statistics", value=status_str, inline=False)

        #structure info
        rs = ctx.guild.roles
        rs.reverse()
        print(rs, type(rs))
        rs_str = ""
        for r in rs:
            rs_str += f"{r.name}\n"
        struct_str = f"**This server uses the {len(rs)} following roles:**\n{rs_str}"
        stats.add_field(name="Server structure", value=struct_str, inline=False)
        await ctx.send(embed=stats)


def setup(bot):
    bot.add_cog(Essentials(bot))
