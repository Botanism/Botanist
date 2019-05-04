import discord
from settings import *
from checks import *

TOKEN = "NTY4MDkyNTY5NTE5NzgzOTM2.XMiBDw.zCL0KhV_gOtxfyACctgYCLcLlEY"
# PREFIX = "g:"

# EMOJIS = {
#     "wastebasket": "\U0001F5D1",
#     "check": "\U00002705",
#     "hourglass": "\U000023F3"
# }

#bot = commands.Bot(command_prefix=PREFIX)

class Todo(commands.Cog):
    """A suite of command to make a nice todo list."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == bot.user:
            return
        await bot.process_commands(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.user_id != bot.user.id:
            message = await bot.get_channel(reaction.channel_id).fetch_message(reaction.message_id)

            with open(TODO_CHANNEL, "r") as file:
                channelId = file.readlines()[0]

            if reaction.channel_id == int(channelId): #Check if it's a todo-message (check if it's the good channel)
                if len(message.embeds) > 0: # Check if it's an embed, I think this will avoid most problems
                    if reaction.emoji.name == EMOJIS['wastebasket']:
                        await bot.get_channel(reaction.channel_id).delete_messages([message])

                        repostFieldValue = None
                        for field in message.embeds[0].fields:
                            if field.name == "Public repost":
                                repostFieldValue = field.value
                        
                        if repostFieldValue != None:
                            repostMessage = await bot.get_channel(int(repostFieldValue.split(':')[0][2:-2])).fetch_message(int(repostFieldValue.split(':')[1][1:]))
                            await repostMessage.delete()
                    elif reaction.emoji.name == EMOJIS['check']:
                        await message.remove_reaction(EMOJIS['hourglass'], bot.user)
                    elif reaction.emoji.name == EMOJIS['hourglass']:
                        await message.remove_reaction(EMOJIS['check'], bot.user)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        message = await bot.get_channel(reaction.channel_id).fetch_message(reaction.message_id)

        with open(TODO_CHANNEL, "r") as file:
            channelId = file.readlines()[0]

        if reaction.channel_id == int(channelId): # Check if it's a todo-message (check if it's the good channel)
            if len(message.embeds) > 0: # Check if it's an embed, I think this will avoid most problems
                if reaction.user_id != bot.user.id:
                    if reaction.emoji.name == EMOJIS['check']:
                        await message.add_reaction(EMOJIS['hourglass'])
                    elif reaction.emoji.name == EMOJIS['hourglass']:
                        await message.add_reaction(EMOJIS['check'])

    @commands.group()
    async def todo(self, ctx):
        '''Commands to manage a todolist.'''
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: See for ``' + PREFIX + 'help todo``')

    @todo.command()
    async def add(self, ctx, *args):
        '''Command to add a todo. Usage : <the thing todo>;<type of todo>;<assigned to / false>;<repost public channel / false>'''
        with open(TODO_CHANNEL, "r") as file:
            channelId = file.readlines()[0]
            if channelId == None or channelId == "":
                await ctx.channel.send("The todos' channel must be selected with the command " + PREFIX + "todo channel")
                return
        channel = bot.get_channel(int(channelId))

        command = ""
        for arg in args:
            command += " {}".format(arg)
        command = command.split(";")

        todoType = None

        with open(TODO_TYPES, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(';')
                if command[1] == line[0]:
                    todoType = line
                    break
        
        if todoType != None:
            embedColor = int(todoType[1], 16)
        else:
            embedColor = 0x28a745
        
        newEmbed = discord.Embed(description=command[0], url="", color=embedColor)
        
        command[2] = command[2].replace(' ', '') #TODO: Use dfind instead ?
        if command[2] != "false":
            if command[2].startswith("<@"):
                user = ctx.guild.get_member(int(command[2][2:-1]))
            else:
                user = ctx.guild.get_member_named(command[2])
            
            if user != None:
                newEmbed.add_field(name="Asssigned to", value=user.mention, inline=True)
        
        if command[3] != "false":
            if command[3].startswith("<#"):
                repostChannel = ctx.guild.get_channel(int(command[3][2:-1]))
            else:
                for chan in ctx.guild.channels:
                    if(chan.name == command[3]):
                        repostChannel = chan
        else:
            repostChannel = None
        
        newEmbed.set_footer(text=command[1])
        if repostChannel != None:
            publicTodo = await repostChannel.send(embed=newEmbed)
            newEmbed.add_field(name="Public repost", value=repostChannel.mention + " : " + str(publicTodo.id), inline=True)
        
        message = await channel.send(embed=newEmbed)
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

        with open(TODO_TYPES, "r+") as file:
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
        with open(TODO_TYPES, "r") as file:
            lines = file.readlines()
        with open(TODO_TYPES, "w") as file:
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
        with open(TODO_TYPES, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(';')
                text += "**" + line[0] + "** - *#"+line[1][2:] + "*\n"

        newEmbed = discord.Embed(description=text, url="", color=0x28a745)
        message = await ctx.channel.send(embed=newEmbed)

    @todo.command()
    async def channel(self, ctx):
        '''Command to select the channel where the todos will be'''
        with open(TODO_CHANNEL, "w") as file:
            file.write(str(ctx.channel.id))
        await ctx.channel.send('Okay ! This channel wil be used for the todos !')

def setup(bot):
    bot.add_cog(Todo(bot))