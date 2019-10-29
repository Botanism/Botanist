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

class ClearanceConfigEntry(ConfigEntry, metaclass=Singleton):
    """docstring for ClearanceConfigEntry"""
    def __init__(self, bot, cfg_chan_id):
        super(ClearanceConfigEntry, self).__init__()

    async def run(self, ctx):
        self.config_channel.send("**\nStarting role configuration**\nThis bot uses two level of clearance for its commands.\nThe first one is the **manager** level of clearance. Everyone with a role with this clearance can use commands related to server management. This includes but is not limited to message management and issuing warnings.\nThe second level of clearance is **admin**. Anyone who has a role with this level of clearance can use all commands but the ones related to the bot configuration. This is reserved to the server owner. All roles with this level of clearance inherit **manager** clearance as well.")

        new_roles = []
        for role_lvl in ROLES_LEVEL:
            retry = True
            while retry:
                new_role = []
                #asking the owner which roles he wants to give clearance to
                roles = await self.get_answer(ctx, f"List all the roles you want to be given the **{role_lvl}** level of clearance.", filters="roles")
                
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


class Config(commands.Cog):
    """a suite of commands meant ot give server admins/owners and easy way to setup the bot's
    preferences directly from discord."""
    def __init__(self, bot):
        self.bot = bot
        #change to make it cross-server
        self.config_channels={}
        #other values can't be added as of now
        self.allowed_answers = {1:["yes", "y"],
                                0:["no", "n"]}


    @commands.Cog.listener()
    async def on_guild_join(guild):
        await self.make_cfg_chan(guild)

    @commands.group()
    @is_server_owner()
    async def cfg(self, ctx):
        self.ad_msg = discord.Embed(description="I ({}) have recently been added to this server! I hope I'll be useful to you. Hopefully you won't find me too many bugs. However if you do I would appreciate it if you could report them to the [server]({}) where my developers are ~~partying~~ working hard to make me better. This is also the place to share your thoughts on how to improve me. Have a nice day and hopefully, see you there {}".format(ctx.me.mention, DEV_SRV_URL, EMOJIS["wave"]))
        if ctx.invoked_subcommand == None:
            await ctx.send(ERR_NO_SUBCOMMAND)


    async def make_cfg_chan(self, ctx_or_guild):
        if type(ctx_or_guild)==discord.Guild: g = ctx_or_guild
        else: g = ctx_or_guild.guild
        overwrite = {
        g.default_role: discord.PermissionOverwrite(read_messages=False),
        g.owner : discord.PermissionOverwrite(read_messages=True)
        }
        self.config_channels[g.id] = await g.create_text_channel("cli-bot-config", overwrites=overwrite)
        return self.config_channels[g.id]


    @cfg.command()
    async def init(self, ctx):
        #creating new hidden channel only the owner can see
        await self.make_cfg_chan(ctx)

        #starting all configurations
        await self.config_channels[ctx.guild.id].send(f'''You are about to start the configuration of {ctx.me.mention}. If you are unfamiliar with CLI (Command Line Interface) you may want to check the documentation on github ({WEBSITE}). The same goes if you don't know the bot's functionnalities''')
        await self.config_channels[ctx.guild.id].send("This will overwrite all of your existing configurations. Do you want to continue ? [y/n]")
        response = await self.bot.wait_for("message", check=self.is_yn_answer)
        if response.content[0].lower() == "n":return False
        await self.config_channels[ctx.guild.id].send("**Starting full bot configuration...**")

        try:
            await self.cfg_poll(ctx)
            await self.config_channels[ctx.guild.id].send("Role setup is **mendatory** for the bot to work correctly. Otherwise no one will be able to use administration commands.")
            await self.cfg_clearance(ctx)
            await self.cfg_welcome(ctx)
            await self.cfg_goodbye(ctx)

            #asking for permisison to advertise
            await self.config_channels[ctx.guild.id].send("You're almost done ! Just one more thing...")
            await self.allow_ad(ctx)


            local_logger.info(f"Setup for server {ctx.guild.name}({ctx.guild.id}) is done")

        except Exception as e:
            await ctx.send(ERR_UNEXCPECTED.format(None))
            await ctx.send("Dropping configuration and rolling back unconfirmed changes.")
            #await self.config_channels[ctx.guild.id].delete(reason="Failed to interactively configure the bot")
            local_logger.exception(e)

        finally:
            await self.config_channels[ctx.guild.id].send("Thank you for inviting our bot and taking the patience to configure it.\nThis channel will be deleted in 10 seconds...")
            await asyncio.sleep(10)
            await self.config_channels[ctx.guild.id].delete(reason="Configuration completed")

    #@cfg.command()
    @is_init()
    async def chg(self, ctx, setting):
        '''doesn't work yet'''
        try:
            print(f"Starting config of extension {setting}")
            await self.make_cfg_chan(ctx)
            exec("await self.cfg_"+setting)

        except Exception as e:
            local_logger.exception(e)

        finally:
            await self.config_channels[ctx.guild.id].send("Thank you for inviting our bot and taking the patience to configure it.\nThis channel will be deleted in 10 seconds...")
            await asyncio.sleep(10)
            await self.config_channels[ctx.guild.id].delete(reason="Configuration completed")

def setup(bot):
    bot.add_cog(Config(bot))