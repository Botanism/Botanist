import os
import logging
import discord
from settings import *
from checks import *

#########################################
#										#
#										#
#			Setting up logging			#
#										#
#										#
#########################################
local_logger = logging.getLogger(__name__)
local_logger.setLevel(LOGGING_LEVEL)
local_logger.addHandler(LOGGING_HANDLER)
local_logger.info("Innitalized {} logger".format(__name__))



#########################################
#										#
#										#
#			Making commands				#
#										#
#										#
#########################################


class Poll(commands.Cog):
	"""TODO: A suite of commands providing users with tools to more easilly get the community's opinion on an idea"""
	def __init__(self, bot):
		self.bot = bot

		#making sure POLL_ALLOWED_CHANNELS_FILE exists
		if POLL_ALLOWED_CHANNELS_FILE not in os.listdir():
			local_logger.warning("{} doesn't exist & not configured".format(POLL_ALLOWED_CHANNELS_FILE))
			with open(POLL_ALLOWED_CHANNELS_FILE, "w") as file:
				pass

		#making poll_allowed channels according to the message's guild
		self.poll_allowed_chans = {}
		with open(POLL_ALLOWED_CHANNELS_FILE, "r") as file:
			for line in file.readlines():
				guild_id = int(line.split(";")[0])
				self.poll_allowed_chans[guild_id] = [int(chan_id) for chan_id in line.split(";")[1:]]


		
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		'''currently makes this checks for ALL channels. Might want to change the behavior to allow reactions on other msgs'''
		if not self.poll_allowed_chans[payload.guild_id]:
			local_logger.warning("Guild [{0.id}] doesn't have any channel for polls".format(payload.guild_id))
			return


		#checking that user isn't the bot
		if (payload.user_id != self.bot.user.id) and (payload.channel_id in self.poll_allowed_chans[payload.guild_id]):

			#checking if reaction is allowed
			if payload.emoji.name not in [EMOJIS["thumbsdown"],EMOJIS["thumbsup"],EMOJIS["shrug"]]:
				#deleting  reaction of the user. Preserves other reactions
				try:
					#I've spent an hour trying to find out if there was a better way to do this
					message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
					user = self.bot.get_user(payload.user_id)

					#iterating over message's reactions to find out which was added
					for reaction in message.reactions:
						#testing if current emoji is the one just added
						if reaction.emoji == payload.emoji.name:
							#removing unauthorized emoji
							await reaction.remove(user)

				except Exception as e:
					local_logger.exception("Couldn't remove reaction {}".format("reaction"))
					raise e


	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author==self.bot.user: return

		if message.channel.id in self.poll_allowed_chans[message.guild.id] and message.content.startswith(PREFIX)!=True:
			embed_poll = discord.Embed(
				title = "{}{}".format(message.author.name, message.author.avatar_url),
				description = message.content,
				colour = discord.Color(7726379),
				url = None
				)

			#embed_poll.set_thumbnail(url=message.author.avatar_url)
			#embed_poll.set_footer(text=message.author.name, icon_url=message.author.avatar_url)

			try:
				await message.delete()
				sent_msg = await message.channel.send(embed=embed_poll)
				await sent_msg.add_reaction(EMOJIS["thumbsup"])
				await sent_msg.add_reaction(EMOJIS["shrug"])
				await sent_msg.add_reaction(EMOJIS["thumbsdown"])

			except Exception as e:
				local_logger.exception("Couldn't send and delete all reaction")

def setup(bot):
	bot.add_cog(Poll(bot))