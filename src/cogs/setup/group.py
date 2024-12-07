import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_group_cog import Base_GroupCog
from cogs.setup.impls.dailymoney_impl import Dailymoney_Impl

class Setup_CommandGroup(Base_GroupCog, group_name = "setup"):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__dailymoney_impl:Dailymoney_Impl = None
        super().__init__(logging.getLogger("cmds.setup"))

    @app_commands.command(name = "dailymoney", description = "Opens the main setup view for the dailymoney configuration")
    async def dailymoney(self, ctx:discord.Interaction):
        await self.__dailymoney_impl.on_command(ctx)

    async def cog_load(self):
        await self.__bot.load_extension("cogs.setup.impls.dailymoney_impl")
        self.__dailymoney_impl = Dailymoney_Impl(self.__bot)
        await self.__dailymoney_impl.load()
        return await super().cog_load()
    
    async def cog_unload(self):
        await self.__dailymoney_impl.unload()
        await self.__bot.unload_extension("cogs.setup.impls.dailymoney_impl")
        return await super().cog_unload()
    
async def setup(bot:commands.Bot):
    await bot.add_cog(Setup_CommandGroup(bot))