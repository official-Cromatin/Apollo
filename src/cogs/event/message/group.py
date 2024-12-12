import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal
from datetime import datetime
from utils.datetime_tools import get_elapsed_time_milliseconds
from cogs.event.message.impls.experience_impl import Experience_Impl
from cogs.event.message.impls.pick_money_impl import PickMoney_Impl
import traceback

class Message_Events(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__experience:Experience_Impl = None
        self.__pick_money:PickMoney_Impl = None

        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("evnt.msg"))

    @commands.Cog.listener()
    async def on_message(self, msg:discord.Message):
        try:
            begin = datetime.now().timestamp()
            # Check if the message comes from the bot itself or a private channel
            if isinstance(msg.channel, discord.channel.DMChannel):
                self._logger.warning("Ignoring message send to bot privately")
                return
            elif msg.author.id == self.__bot.user.id:
                return

            # Check what kind of functionality is enabled for that channel
            functionality = await self.__portal.database.get_channel_functionality(msg.channel.id)
        
            if functionality:
                if functionality[0]: # Experience
                    await self.__experience.handle(msg)

                if functionality[1]: # Pick money
                    await self.__pick_money.handle(msg)

                self._logger.debug(f"Handled {sum(functionality)} functionalities in {get_elapsed_time_milliseconds(datetime.now().timestamp() - begin)} for {msg.channel.name} ({msg.channel.id}) send by {msg.author.name} ({msg.author.id})")
            else:
                self._logger.debug(f"No functionalities for {msg.channel.name} ({msg.channel.id}) defined")
        except Exception as error:
            traceback.print_exception(type(error), error, error.__traceback__)

    async def cog_load(self):
        await self.__bot.load_extension("cogs.event.message.impls.experience_impl")
        self.__experience = Experience_Impl(self.__bot)
        await self.__bot.load_extension("cogs.event.message.impls.pick_money_impl")
        self.__pick_money = PickMoney_Impl(self.__bot)
        return await super().cog_load()

    async def cog_unload(self):
        await self.__bot.unload_extension("cogs.event.message.impls.experience_impl")
        await self.__bot.unload_extension("cogs.event.message.impls.pick_money_impl")
        return await super().cog_unload()

async def setup(bot: commands.Bot):
    await bot.add_cog(Message_Events(bot))