from discord.ext import commands
import discord
import logging
from utils.portal import Portal
import random
from pathlib import Path

class PickMoney_Impl:
    def __init__(self, bot:commands.Bot) -> None:
        self.__bot = bot
        self.__logger = logging.getLogger("evnt.msg.pickmoney")
        self.__portal = Portal.instance()

    async def handle(self, msg:discord.Message):
        # Load settings for the pick money channel
        channel_settings:tuple = await self.__portal.database.get_pick_money_settings(msg.channel.id)
        if channel_settings is None:
            self.__logger.error(f"Channel {msg.channel.name} (ID: {msg.channel.id}, GUILD: {msg.guild.name}) has activated the apperance of pick money, but no settings could be found. Was there a problem saving?")
            return
        min_amount, max_amount, probability = channel_settings

        # Randomize if the message is going to appear and the amount of money
        if random.randint(1, probability) != 1:
            return 
        amount = random.randint(min_amount, max_amount)

        # Create and send the embed
        file_path = Path(self.__portal.source_path) / "assets" / "img1.jpg"
        attatchment_image = discord.File(file_path)
        message = await msg.channel.send(
            content = f"`{amount}` :dollar: have appeared randomly, collect them by typing `/pick`, quick!",
            file = attatchment_image
        )

        # Create the entry in the database
        await self.__portal.database.create_pick_message(msg.guild.id, msg.channel.id, message.id, amount)
        self.__logger.debug(f"In the channel {msg.channel.name} with the chance 1/{probability}, {amount} dollars have appeared randomly")


async def setup(bot):
    pass