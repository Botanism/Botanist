import logging
import os
import json
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
    if f"{ctx.guild.id}.json" in os.listdir(CONFIG_FOLDER):
        return True
    return False

def has_auth(clearance, *args):
    '''checks whether the user invoking the command has the specified clearance level of clearance for the server the command is being ran on'''
    def predicate(ctx):
        with ConfigFile(ctx.guild.id, folder=CONFIG_FOLDER) as c:
            allowed_roles = c["roles"][clearance]
            print(allowed_roles)
            for role in ctx.author.roles:
                if role.id in allowed_roles:
                    return True
            local_logger.send(ERR_UNSUFFICIENT_PRIVILEGE)
            local_logger.warning(ERR_UNSUFFICIENT_PRIVILEGE)
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

def assert_struct():
    try:
        files = os.listdir()
        to_make = [SLAPPING_FOLDER, TODO_FOLDER, CONFIG_FOLDER]
        for folder in to_make:
            if folder not in files:
                os.mkdir(folder)
        return True

    except Exception as e:
        local_logger.exception(e)
        raise e
        return False

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
                assert fext=="json", local_logger.error(f'''Can't load file with extension: {fext}''')
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