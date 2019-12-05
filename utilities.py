from collections import OrderedDict
import logging
import os
import json
import datetime
import discord
from settings import *
from discord.ext import commands
from collections import UserDict

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
local_logger.info(f"Innitalized {__name__} logger")


#########################################
#                                       #
#                                       #
#               Checks                  #
#                                       #
#                                       #
#########################################

def is_runner(): # to be deleted sine it does the same as is_owner()
    def check_condition(ctx):
        return ctx.message.author.id ==RUNNER_ID
    result = commands.check(check_condition)
    if result == False:
        pass
        #ctx.send(ERR_UNSUFFICIENT_PRIVILEGE)
    return result

def is_init():
    '''checks whether the server has been initialized. Meant as a fale-safe for commands requiring configuration.'''
    def check_condition(ctx):
        conf_files = os.listdir(CONFIG_FOLDER)
        file_name = f"{ctx.guild.id}.json"
        #ctx.send(ERR_NOT_SETUP)
        return file_name in conf_files

    return commands.check(check_condition)

def was_init(ctx):
    '''same as the previous function except this one isn't a decorator. Mainly used for listenners'''
    return f"{ctx.guild.id}.json" in os.listdir(CONFIG_FOLDER)

def has_auth(clearance, *args):
    '''checks whether the user invoking the command has the specified clearance level of clearance for the server the command is being ran on'''
    def predicate(ctx):
        with ConfigFile(ctx.guild.id, folder=CONFIG_FOLDER) as c:
            allowed_roles = c["roles"][clearance]
            for role in ctx.author.roles:
                if role.id in allowed_roles:
                    return True
            local_logger.send(ERR_UNSUFFICIENT_PRIVILEGE)
            local_logger.warning(ERR_UNSUFFICIENT_PRIVILEGE)
            #await ctx.send(embed=get_embed_err(ERR_UNSUFFICIENT_PRIVILEGE))
            return False

    return commands.check(predicate)

def is_server_owner():
    '''check meant to verify whether its author os the owner of the server where the command is being ran'''
    def predicate(ctx):
        if ctx.author == ctx.guild.owner:
            return True
        #ctx.send(ERR_UNSUFFICIENT_PRIVILEGE)
        return False

    return commands.check(predicate)


#########################################
#                                       #
#                                       #
#           Utilities                   #
#                                       #
#                                       #
#########################################

def get_embed_err(error):
    err_embed = discord.Embed(
        title = f"""{EMOJIS["warning"]} **Command Error:** """ + error[0],
        description = error[1],
        color = 16729127)
    return err_embed



def assert_struct(guilds):
    try:
        files = os.listdir()
        to_make = [SLAPPING_FOLDER, TODO_FOLDER, CONFIG_FOLDER]
        for folder in to_make:
            if folder not in files:
                os.mkdir(folder)
        
        for folder in [CONFIG_FOLDER, SLAPPING_FOLDER]:
            g_folder = os.listdir(folder)
            for g in guilds:
                if str(g.id)+".json" not in g_folder:
                    local_logger.warning(f"Missing config file for {g}!")
                    with open(os.path.join(CONFIG_FOLDER, str(g.id)+".json"), "w") as file:
                        json.dump(DEFAULT_SERVER_FILE)

        return True

    except Exception as e:
        local_logger.exception(e)
        raise e
        return False

time_seps = ["d", "h", "m", "s"]
DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def to_datetime(argument, sub=True):
    times = OrderedDict([('y', 0), ('M', 0), ('d', 0), ('h', 0), ('m', 0), ('s', 0)])

    last = 0
    for char, i in zip(argument, range(len(argument))):
        if char not in DIGITS:
            if char in time_seps:
                times[char] = int(argument[last:i])
                last = i+1
            else:
                return False
        else:
            continue

    diff = datetime.timedelta(days=times["d"], hours=times["h"], minutes=times["m"], seconds=times["s"])
    if sub:
        return datetime.datetime.now() - diff
    else:
        return diff


class Singleton(type):
    """a metaclass that makes your class a a singleton"""
    _instances = {} #dict so that different classes can inherit from the metaclass
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigFile(UserDict):
            """A class representing a json config file. Used to handle configuration information.
            
            file:   the file name without the extension. This is usually the ID of the guild it represents
            folder: the folder to read the file from. This represents the kind of data handled
            fext:   the file extension. Only supports "json" for now
            force:  creates the file if not found
            """
            def __init__(self, file, folder=CONFIG_FOLDER, fext="json", force=True):
                super(ConfigFile, self).__init__()
                #since the ID is an int -> making sure it is considered as a string
                self.file = str(file)

                self.folder = folder
                self.fext = fext
                self.force = force

                #currently only supports "json" files
                #assert fext=="json", local_logger.error(f'''Can't load file with extension: {fext}''')
                #if the extension is correct -> appending the extension name to the filename
                self.file+= "." + self.fext
                #making path
                self.path = os.path.join(self.folder, self.file)
                #self.last_m_time = os.path.getmtime(self.path)


            def __enter__(self):
                self.make_file()
                self.read()
                return self

            def __exit__(self, *args):
                self.save()

            def make_file(self):
                files = os.listdir(self.folder)
                #print(self.file not in files)
                if self.file not in files:
                    if not self.force: return False
                    with open(os.path.join(self.folder,self.file), "w") as file:
                        pass #creating empty file
                return True

            def save(self):
                '''makes the file from the dict'''
                try:
                    with open(self.path, "w") as file:
                        json.dump(self.data, file)

                except Exception as e:
                    local_logger.exception(e)
                    raise e

            def read(self):
                '''builds the dict from the file '''
                try:
                    if not self.make_file: return self.data
                
                    with open(os.path.join(self.folder, self.file), "r") as file:
                        self.data = json.load(file)
                
                    return self.data

                except Exception as e:
                    local_logger.exception(e)
                    raise e


class Translator(object):
    """docstring for Translator
    lang can either be a 2-chars long string or a Context object"""
    def __init__(self, ext, lang, help_type=False):
        self.ext = ext
        self.lang = self.get_lang(lang)

        if help_type:
            name = "help"
        else:
            name = "strings"

        self.file = os.path.join("lang", ext, name+self.lang)

    def load_strings(self):
        with open(self.file, "r") as translation:
            return json.load(translation)

    def get_lang(self, lang):
        if isinstance(lang, str):
            return lang

        elif isinstance(lang, discord.ext.commands.Context):
            with ConfigFile(lang.guild.id, force=False) as conf:
                return conf["lang"]

        else:
            raise TypeError("lang must be <str> or <discord.ext.commands.Context> not {}".format(type(lang)))


class ConfigEntry():
    """A generic configuration class that must subclasses to be used correctly in each extension."""
    def __init__(self, bot, cfg_chan_id):
        self.bot = bot
        #only a single config channel because the class can have several instances, each for a different server
        self.config_channel = cfg_chan_id
        self.allowed_answers = {
        1: ["yes", "y"],
        0: ["no", "n"]
        }


    def is_answer(self, ctx):
        if ctx.channel == self.config_channel: return True
        return False

    def is_yn_answer(self, ctx):
        correct_answers = []
        for i in self.allowed_answers:
            for ans in self.allowed_answers[i]:
                correct_answers.append(ans)

        if self.is_answer(ctx) and (ctx.content.lower() in correct_answers): return True
        return False

    async def get_yn(self, ctx, question):
        await ctx.send(question+" [y/n]")
        response = await self.bot.wait_for("message", check=self.is_yn_answer)

        if response.content.lower() in self.allowed_answers[0]:
            return False
        else:
            return True

    async def get_answer(self, ctx, question, filters=[]):
        await ctx.send(question)
        answered = False
        while not answered:
            response = await self.bot.wait_for("message", check=self.is_answer)

            if filters:
                cat = self.filter_msg(response)
                complete = True
                for filt in filters:
                    if not cat[filt]:
                        cat.pop(filt)
                        complete = False # -> remove bc sometimes you need to accept no mention?

                if complete:
                    if len(filters)==1:
                        return cat[filters[0]]
                    else:
                        return cat


            else:
                return response

            await ctx.send(question)


    def filter_msg(self, msg):
        #assert filters != None, TypeError("You must set filters to filter a message.")

        results = {
        "roles": msg.role_mentions,
        "mentions": msg.mentions,
        "channels": msg.channel_mentions,
        }

        return results

    async def run(self, ctx):
        """this functions serves as placeholder for the instances which should override it"""
        pass
