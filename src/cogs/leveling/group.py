import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_group_cog import Base_GroupCog
from cogs.leveling.impls.setup_impl import Setup_Impl
from cogs.leveling.impls.configure_impl import Configure_Impl

class Leveling_CommandGroup(Base_GroupCog, group_name = "leveling"):
    def __init__(self, bot:commands.Bot):
        self.__setup:Setup_Impl = None
        self.__configure:Configure_Impl = None

        self.__bot = bot
        super().__init__(logging.getLogger("cmds.leveling"))

    @app_commands.command(name = "setup")
    async def setup(self, ctx:discord.Interaction):
        await self.__setup.on_command(ctx)


    async def cog_load(self):
        await self.__bot.load_extension("cogs.leveling.impls.configure_impl")
        self.__configure = Configure_Impl(self.__bot)
        await self.__configure.on_load()

        await self.__bot.load_extension("cogs.leveling.impls.setup_impl")
        self.__setup = Setup_Impl(self.__bot, self.__configure)
        await self.__setup.on_load()

        return await super().cog_load()
    
    async def cog_unload(self):
        await self.__setup.on_unload()
        await self.__bot.unload_extension("cogs.leveling.impls.setup_impl")

        await self.__configure.on_unload()
        await self.__bot.unload_extension("cogs.leveling.impls.configure_impl")

        return await super().cog_unload()


async def setup(bot:commands.Bot):
    await bot.add_cog(Leveling_CommandGroup(bot))
