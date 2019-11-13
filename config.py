import logging
import discord
import asyncio
import os
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

class ClearanceConfigEntry(ConfigEntry):
    """docstring for ClearanceConfigEntry"""
    def __init__(self, bot, cfg_chan_id):
        super().__init__(bot, cfg_chan_id)

    async def run(self, ctx):
        try:
            await self.config_channel.send("**\nStarting role configuration**\nThis bot uses two level of clearance for its commands.\nThe first one is the **manager** level of clearance. Everyone with a role with this clearance can use commands related to server management. This includes but is not limited to message management and issuing warnings.\nThe second level of clearance is **admin**. Anyone who has a role with this level of clearance can use all commands but the ones related to the bot configuration. This is reserved to the server owner. All roles with this level of clearance inherit **manager** clearance as well.")

            new_roles = []
            for role_lvl in ROLES_LEVEL:
                retry = True
                while retry:
                    new_role = []
                    #asking the owner which roles he wants to give clearance to
                    roles = await self.get_answer(ctx, f"List all the roles you want to be given the **{role_lvl}** level of clearance.", filters=["roles"])
                    print(roles)

                    #making sure at least a role was selected
                    if len(roles)==0:
                        await self.config_channel.send(f"You need to set at least one role for the {role_lvl} clearance.")
                        continue

                    #building role string
                    roles_str = ""
                    for role in roles:
                        roles_str += f" {role.mention}"

                    #asking for confirmation
                    confirmed = await self.get_yn(ctx, f"You are about to give{roles_str} roles the **{role_lvl}** level of clearance. Do you confirm this ?")
                    if not confirmed:
                        again = await self.get_yn(ctx, f"Aborting configuration of {role_lvl}. Do you want to retry?")
                        if not again:
                            local_logger.info(f"The configuration for the {role_lvl} clearance has been cancelled for server {ctx.guild.name}")
                            retry = False

                    else:
                        retry = False

                local_logger.info(f"Server {ctx.guild.name} configured its {role_lvl} roles")
                for role in roles:
                    new_role.append(role.id)

                #adding to master role list
                new_roles.append(new_role)

            #giving admin roles the manager clearance
            for m_role in new_roles[1]:
                new_roles[0].append(m_role)

            with ConfigFile(ctx.guild.id) as conf:
                conf["roles"]["manager"] = new_roles[0]
                conf["roles"]["admin"] = new_roles[1]    

            await self.config_channel.send("Successfully updated role configuration")

        except Exception as e:
            raise e

class Config(commands.Cog, ConfigEntry):
    """a suite of commands meant ot give server admins/owners and easy way to setup the bot's
    preferences directly from discord."""
    def __init__(self, bot):
        self.config_entry = ClearanceConfigEntry
        self.config_channels={}
        self.bot = bot
        self.allowed_answers = {
        1: ["yes", "y"],
        0: ["no", "n"]
        }

    @commands.Cog.listener()
    async def on_guild_join(guild):
        await self.make_cfg_chan(guild)

    async def make_cfg_chan(self, ctx_or_guild):
        if type(ctx_or_guild)==discord.Guild: g = ctx_or_guild
        else: g = ctx_or_guild.guild
        overwrite = {
        g.default_role: discord.PermissionOverwrite(read_messages=False),
        g.owner : discord.PermissionOverwrite(read_messages=True)
        }
        self.config_channels[g.id] = await g.create_text_channel("cli-bot-config", overwrites=overwrite)
        return self.config_channels[g.id]


    @commands.command()
    async def init(self, ctx):
        await self.make_cfg_chan(ctx)
        self.config_channel = self.config_channels[ctx.guild.id]
        #creating new hidden channel only the owner/admins can see
        ctx.channel = self.config_channel

        #starting all configurations
        await self.config_channels[ctx.guild.id].send(f'''You are about to start the configuration of {ctx.me.mention}. If you are unfamiliar with CLI (Command Line Interface) you may want to check the documentation on github ({WEBSITE}). The same goes if you don't know the bot's functionnalities''')
        pursue = await self.get_yn(ctx, "This will overwrite all of your existing configurations. Do you want to continue ?")
        if not pursue: return False

        await self.config_channels[ctx.guild.id].send("**Starting full bot configuration...**")

        try:
            await self.config_channels[ctx.guild.id].send("Role setup is **mendatory** for the bot to work correctly. Otherwise no one will be able to use administration commands.")
            #await ClearanceConfigEntry(self.bot, self.config_channel).run(ctx)

            for cog in self.bot.cogs:
                if self.bot.cogs[cog].config_entry:
                    await self.bot.cogs[cog].config_entry(self.bot, self.config_channel).run(ctx)

            #asking for permisison to advertise
            await self.config_channels[ctx.guild.id].send("You're almost done ! Just one more thing...")
            await self.allow_ad(ctx)


            local_logger.info(f"Setup for server {ctx.guild.name}({ctx.guild.id}) is done")

        except Exception as e:
            raise e
            await ctx.send(embed=get_embed_err(ERR_UNEXCPECTED.format(str(e))))
            await ctx.send("Dropping configuration and rolling back unconfirmed changes.")
            local_logger.exception(e)

        except:
            raise

        finally:
            await self.config_channels[ctx.guild.id].send("Thank you for inviting our bot and taking the patience to configure it.\nThis channel will be deleted in 10 seconds...")
            await asyncio.sleep(10)
            await self.config_channels[ctx.guild.id].delete(reason="Configuration completed")

    async def allow_ad(self, ctx):
        self.ad_msg = discord.Embed(description="I ({}) have recently been added to this server! I hope I'll be useful to you. Hopefully you won't find me too many bugs. However if you do I would appreciate it if you could report them to the [server]({}) where my developers are ~~partying~~ working hard to make me better. This is also the place to share your thoughts on how to improve me. Have a nice day and hopefully, see you there {}".format(ctx.me.mention, DEV_SRV_URL, EMOJIS["wave"]))
        try:
            allowed = await self.get_yn(ctx, "Do you allow me to send a message in a channel of your choice? This message would give out a link to my development server. It would allow me to get more feedback. This would really help me pursue the development of the bot. If you like it please think about it.")
            if not allowed: return False

            chan = await self.get_answer(ctx, "Thank you very much ! In which channel do you want me to post this message?", filters=["channels"])

            with ConfigFile(ctx.guild.id) as conf:
                conf["advertisement"] = chan[0].id

            await chan.send(embed=self.ad_msg)

        except Exception as e:
            local_logger.exception(e)
            raise e

def setup(bot):
    bot.add_cog(Config(bot))