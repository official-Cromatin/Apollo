from discord.ext import commands
import discord
import logging
from utils.portal import Portal

class Experience_Impl:
    def __init__(self, bot:commands.Bot) -> None:
        self.__bot = bot
        self.__logger = logging.getLogger("evnt.msg.experience")
        self.__portal = Portal.instance()

    async def handle(self, msg:discord.Message):
        # Check if the user is applicable for getting experience
        if await self.__portal.database.user_for_experience_applicable(msg.guild.id, msg.author.id) == False:
            return
        await self.__portal.database.reset_user_experience_gain(msg.guild.id, msg.author.id)

        # Load settings for the experience channel
        channel_settings:tuple = await self.__portal.database.get_experience_settings(msg.channel.id)
        if channel_settings is None:
            self.__logger.error(f"Channel {msg.channel.name} (ID: {msg.channel.id}, GUILD: {msg.guild.name}) has activated the gain of experience, but no settings could be found. Was there a problem saving?")
            return
        multiplier, minimum_threshold, maximum_experience = channel_settings

        # Get length of message and multiply with multiplier
        experience = len(msg.content) * multiplier
        if experience < minimum_threshold:
            return
        if experience > maximum_experience:
            experience = maximum_experience
        
        # Add to users experience
        leveled_up, user_lvl, user_xp = await self.__portal.database.add_to_user_experience(msg.guild.id, msg.author.id, experience)
        additonal_log = ""
        if leveled_up:
            embed = discord.Embed(
                description = f"Congratulations <@{msg.author.id}>, you have reached level {user_lvl}!"
            )
            await msg.channel.send(embed = embed)
            additonal_log = " and did level up!"
        self.__logger.debug(f"User {msg.author.name} has gained {experience}{additonal_log} (current xp: {user_xp}) by sending a message into the {msg.channel.name} channel")


async def setup(bot):
    pass