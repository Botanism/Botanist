import logging
from settings import *
import discord
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

class RoleConfigEntry(ConfigEntry):
    """user can choose which roles are "free" """
    def __init__(self, bot, config_chan_id):
        super().__init__(bot, config_chan_id)

    async def run(self, ctx):
        try:
            await ctx.send("\n**Starting free roles configuration**")
            free_roles = []
            pursue = await self.get_yn(ctx, "Free roles can be gotten by everyone using the `role add` command. Do you want to set some?")
            while pursue:
                proles = await self.get_answer(ctx, '''List all the roles you want to be "free".''')
                roles = []
                for role in proles.content.split(" "):
                    try:
                        print(role)
                        roles.append(await discord.ext.commands.RoleConverter().convert(ctx, role))
                    except:
                        pass
                        #raise discord.ext.commands.ArgumentParsingError(f"Couldn't find role {role}")

                roles_str = ""
                for role in roles:
                    print("building the string")
                    roles_str += f" {role.name}"
                agrees = await self.get_yn(ctx, f'''You are about to set {roles_str} as "free" roles. Are you sure?''')
                
                if not agrees:
                    retry = await self.get_yn(ctx, "Do you want to retry?")
                    if retry:
                        continue
                    else:
                        pursue = False

                else:
                    pursue = False
                    with ConfigFile(ctx.guild.id) as conf:
                        print(roles)
                        print([role.id for role in roles])
                        conf["free_roles"] = [role.id for role in roles]
        except:
            raise

class Role(commands.Cog):
    """role management utility. Requires a Gestion role"""
    def __init__(self, bot):
        self.bot = bot
        self.config_entry = RoleConfigEntry

    @commands.group()
    async def role(self, ctx):
        '''role management utility. Requires a Gestion role'''
        if ctx.invoked_subcommand is None:
            local_logger.warning("User didn't provide any subcommand")
            await ctx.send("NotEnoughArguments:\tYou must provide a subcommand")

    @role.command()
    async def add(self, ctx, member: discord.Member, *roles:discord.Role):
        '''Gives <member> listed <roles> roles'''
        #checking if member can self-assing role(s)
        if not has_auth("admin")(ctx):
            allowed_roles = []
            with ConfigFile(ctx.guild.id) as conf:
                for role in roles:
                    if str(role.id) in conf["free_roles"]:
                        allowed_roles.append(role)
                    else:
                        await ctx.send(f"You're not allowed to give yourself the {role.name} role. Ask a moderator if you think this is wrong.")

        else:
            allowed_roles = roles

        if len(allowed_roles)==0:
            local_logger.warning("User didn't provide a role")
            await ctx.send("NotEnoughArguments:\tYou must provide at least one `role`")

        else:
            try:
                await member.add_roles(*allowed_roles)
                roles_str = ""
                for role in allowed_roles:
                    roles_str+= f" {role}"

                await ctx.send(f"You gave {member.name} {roles_str} role(s).")
            except Exception as e:
                local_logger.exception("Couldn't add {} to {}".format(allowed_roles, member))
                await ctx.send("An unexpected error occured !\nTraceback:```python\n{}```".format(e))

    @role.command()
    async def rm(self, ctx, member:discord.Member, *roles:discord.Role):
        '''Removes <member>'s <roles> roles'''
        if len(roles)==0:
            local_logger.warning("User didn't provide a role")
            await ctx.send("NotEnoughArguments:\tYou must provide at least one `role`")

        else:
            try:
                await member.remove_roles(*roles)
            except Exception as e:
                local_logger.exception("Couldn't remove roles ")
                await ctx.send("An unexpected error occured !\nTraceback:```python\n{}```".format(e))


def setup(bot):
    bot.add_cog(Role(bot))