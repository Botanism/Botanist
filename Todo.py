import logging
import discord
from settings import *
from checks import *

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
                            if field.name == PUBLIC_REPOST:
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
    @commands.has_any_role(*GESTION_ROLES, *ADMIN_ROLE)
    async def todo(self, ctx):
        '''Commands to manage a todolist.'''
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: See for ``' + PREFIX + 'help todo``')

    @todo.command()
    async def add(self, ctx, *args):
        '''Command to add a todo. Usage : <the thing todo>;<type of todo>;<assigned to / false>;<repost public channel / false>'''
        with open(TODO_CHANNEL_FILE , "r") as file:
            channel_id = file.readline()
            if channel_id == None or channel_id == "":
                await ctx.channel.send("The todos' channel must be selected with the command " + PREFIX + "todo channel")
                return
        channel = self.bot.get_channel(int(channel_id))

        command = ""
        for arg in args:
            command += " {}".format(arg)
        command = command.split(";")

        todo_type = None

        with open(TODO_TYPES_FILE, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(';')
                if command[1] == line[0]:
                    todo_type = line
                    break
        
        if todo_type != None:
            embed_color = int(todo_type[1], 16)
        else:
            embed_color = 0x28a745
        
        new_embed = discord.Embed(description=command[0], url="", color=embed_color)
        
        command[2] = command[2].replace(' ', '') #TODO: Use dfind instead ?
        if command[2] != "false":
            if command[2].startswith("<@"):
                user = ctx.guild.get_member(int(command[2][2:-1]))
            else:
                user = ctx.guild.get_member_named(command[2])
            
            if user != None:
                new_embed.add_field(name="Asssigned to", value=user.mention, inline=True)
        
        if command[3] != "false":
            if command[3].startswith("<#"):
                repost_channel = ctx.guild.get_channel(int(command[3][2:-1]))
            else:
                for chan in ctx.guild.channels:
                    if(chan.name == command[3]):
                        repost_channel = chan
        else:
            repost_channel = None
        
        new_embed.set_footer(text=command[1])
        if repost_channel != None:
            public_todo = await repost_channel.send(embed=new_embed)
            new_embed.add_field(name=PUBLIC_REPOST, value=repost_channel.mention + " : " + str(public_todo.id), inline=True)
        
        message = await channel.send(embed=new_embed)
        await message.add_reaction(EMOJIS['wastebasket'])
        await message.add_reaction(EMOJIS['check'])
        await message.add_reaction(EMOJIS['hourglass'])
        await ctx.message.delete()

    @todo.command()
    async def addtype(self, ctx, command):
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
    async def removetype(self, ctx, command):
        '''Command to add a remove type.'''
        with open(TODO_TYPES_FILE, "r") as file:
            lines = file.readlines()
        with open(TODO_TYPES_FILE, "w") as file:
            deleted=False
            for line in lines:
                line = line.split(";")
                if line[0] != command:
                    file.write(';'.join(line))
                else:
                    deleted=True
        
        if deleted:
            await ctx.send('Todo type **'+command+'** deleted')
        else:
            await ctx.send('There is no type named **'+command+'**')

    @todo.command()
    async def listtypes(self, ctx):
        '''Command to list all the todo types.'''
        text = "**Type** - *Color*\n\n"
        with open(TODO_TYPES_FILE, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(';')
                text += "**" + line[0] + "** - *#"+line[1][2:] + "*\n"

        new_embed = discord.Embed(description=text, url="", color=0x28a745)
        message = await ctx.channel.send(embed=new_embed)

    @todo.command()
    async def channel(self, ctx):
        '''Command to select the channel where the todos will be'''
        with open(TODO_CHANNEL_FILE , "w") as file:
            file.write(str(ctx.channel.id))
        await ctx.channel.send('Okay ! This channel wil be used for the todos !')

def setup(bot):
    bot.add_cog(Todo(bot))
    