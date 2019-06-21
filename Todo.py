import logging
import discord
from typing import Union
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

class Todo(commands.Cog):
    """A suite of command to make a nice todo list."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.user_id != self.bot.user.id:
            message = await self.bot.get_channel(reaction.channel_id).fetch_message(reaction.message_id)

            with open(TODO_CHANNEL_FILE , "r") as file:
                channel_id = file.readline()

            if reaction.channel_id == int(channel_id): #Check if it's a todo-message (check if it's the good channel)
                if len(message.embeds) > 0: # Check if it's an embed, I think this will avoid most problems
                    if reaction.emoji.name == EMOJIS['wastebasket']:
                        await self.bot.get_channel(reaction.channel_id).delete_messages([message])

                        repost_field_value = None
                        for field in message.embeds[0].fields:
                            if field.name == "Public repost":
                                repost_field_value= field.value
                        
                        if repost_field_value!= None:
                            repost_message = await self.bot.get_channel(int(repost_field_value.split(':')[0][2:-2])).fetch_message(int(repost_field_value.split(':')[1][1:]))
                            await repost_message.delete()
                    elif reaction.emoji.name == EMOJIS['check']:
                        await message.remove_reaction(EMOJIS['hourglass'], self.bot.user)
                    elif reaction.emoji.name == EMOJIS['hourglass']:
                        await message.remove_reaction(EMOJIS['check'], self.bot.user)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        message = await self.bot.get_channel(reaction.channel_id).fetch_message(reaction.message_id)

        with open(TODO_CHANNEL_FILE , "r") as file:
            channel_id = file.readline()

        if reaction.channel_id == int(channel_id): # Check if it's a todo-message (check if it's the good channel)
            if len(message.embeds) > 0: # Check if it's an embed, I think this will avoid most problems
                if reaction.user_id != self.bot.user.id:
                    if reaction.emoji.name == EMOJIS['check']:
                        await message.add_reaction(EMOJIS['hourglass'])
                    elif reaction.emoji.name == EMOJIS['hourglass']:
                        await message.add_reaction(EMOJIS['check'])

    @commands.group()
    @has_auth("manager")
    async def todo(self, ctx):
        '''Commands to manage a todolist.'''
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: See for ``' + PREFIX + 'help todo``')

    @todo.command()
    async def add(self, ctx, todo_type, assignee: Union[bool, discord.Member], repost:Union[bool, discord.TextChannel], *args):
        '''Command to add a todo. Usage : <the thing todo>;<type of todo>;<assigned to / false>;<repost public channel / false>'''

        todo_dict = get_todo(ctx.guild.id)
        
        #making sure the type is valid
        if todo_type not in todo_dict["todo_types"]:
            await ctx.send("Can't assign to an unexisting type. To get a list of available types run `::todo listtypes`.")
            return

        else:
            print(todo_dict["todo_types"][todo_type][1])
            #the color value is saved as an hexadecimal value so it is made an int to get the base 10 decimal value
            embed_color = int(todo_dict["todo_types"][todo_type], 16)
            print(embed_color)

        #building the todo name string
        crt_todo = ""
        for word in args:
            crt_todo+= word

        #building the embed
        new_embed = discord.Embed(description=crt_todo, color=embed_color)
        new_embed.set_footer(todo_type)

        if repost:
            public_todo = await repost.send(embed=new_embed)
            new_embed.add_field(name="Public repost", value=repost.mention+" : "+ str(public_todo.id), inline=True)

        #sending message and reactions
        msg = await ctx.send(embed=new_embed)
        await message.add_reaction(EMOJIS['wastebasket'])
        await message.add_reaction(EMOJIS['check'])
        await message.add_reaction(EMOJIS['hourglass'])        


    @todo.command()
    async def addtype(self, ctx, todo_type, hex_color):
        '''Command to add a todo type.'''
        command = command.split(";")

        if command[1].startswith("#"):
            command[1] = command[1][1:]
        if len(command[1]) != 6:
            if len(command[1]) != 3:
                await ctx.send('The color must be in hexadecimal, like this **#ccc** or **#ff0000**')
                return
            else:
                command[1] = command[1]+command[1]
        color = "0x" + command[1]

        with open(TODO_TYPES_FILE, "r+") as file:
            content = file.readlines()
            for line in content:
                line = line.split(";")
                if line[0] == command[0]:
                    await ctx.send('There is already a type named **'+command[0]+'**')
                    return
            
            file.write('\n' + command[0] + ';' + color)
        await ctx.send('You added the label "'+command[0]+'", the embed\'s color for this todo type will be : #' + command[1])

    @todo.command()
    async def removetype(self, ctx, todo_type):
        '''deletes the <todo_type> type'''
        try:
            old_conf = get_conf(ctx.guild.id)
            print(old_conf["todo_types"])
            #checking whether the type exists in the db
            if todo_type not in old_conf["todo_types"]:
                await ctx.send("Can't delete an unexisting type.")
                return

            old_conf["todo_types"].pop(todo_type)
            update_conf(ctx.guild.id, old_conf)
            await ctx.send(f"Successfully deleted {todo_type} type.")

        except Exception as e:
            local_logger.exception(e)
            await ctx.send(ERR_UNEXCPECTED)

    @todo.command()
    async def listtypes(self, ctx):
        '''Lists all available types'''
        conf = get_conf(ctx.guild.id)
        text = ""
        for t in conf["todo_types"]:
            text += f'''\n**{t}** - \t*#{conf["todo_types"][t]}*'''

        new_embed = discord.Embed(title="**Type** - *Color*", description=text, color=0x28a745)
        await ctx.send(embed=new_embed)

def setup(bot):
    bot.add_cog(Todo(bot))
    