import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_group_cog import Base_GroupCog
from cogs.leveling.impls.setup_impl import Setup_Impl
from cogs.leveling.impls.configure_impl import Configure_Impl
from cogs.leveling.impls.copy_impl import Copy_Impl
from cogs.leveling.impls.info_impl import Info_Impl

class Leveling_CommandGroup(Base_GroupCog, group_name = "leveling"):
    def __init__(self, bot:commands.Bot):
        self.__setup:Setup_Impl = None
        self.__configure:Configure_Impl = None
        self.__copy:Copy_Impl = None
        self.__info:Info_Impl = None

        self.__bot = bot
        super().__init__(logging.getLogger("cmds.leveling"))

    @app_commands.command(name = "setup", description = "Opens the setup wizard for this channel")
    async def setup(self, ctx:discord.Interaction):
        await self.__setup.on_command(ctx)

    @app_commands.command(name = "configure", description = "Changes the settings for the last configuration message")
    @app_commands.describe(
        default_multiplier = "Multiplier, being multiplied by the length of the message",
        minimum_threshold = "Threshold above which the user is rewarded",
        maximum_experience = "Limit for the maximum amount of receivable experience")
    async def configure(self, ctx:discord.Integration, default_multiplier:float = None, minimum_threshold:int = None, maximum_experience:int = None):
        await self.__configure.on_command(ctx, default_multiplier, minimum_threshold, maximum_experience)

    @app_commands.command(name = "copy", description = "Copies the configuration from another channel")
    @app_commands.describe(channel = "Name of the channel from which you want to copy the configuration")
    async def copy(self, ctx:discord.Interaction, channel:str):
        await self.__copy.on_command(ctx, channel)

    @app_commands.command(name = "info", description = "Displays information for this channel, without being able to make changes")
    @app_commands.describe(channel = "Name of the channel of wich you want to display the configuration")
    async def info(self, ctx:discord.Interaction, channel:discord.TextChannel = None):
        await self.__info.on_command(ctx, channel)

    async def cog_load(self):
        await self.__bot.load_extension("cogs.leveling.impls.shared_functions")

        await self.__bot.load_extension("cogs.leveling.impls.configure_impl")
        self.__configure = Configure_Impl(self.__bot)
        await self.__configure.on_load()

        await self.__bot.load_extension("cogs.leveling.impls.copy_impl")
        self.__copy = Copy_Impl(self.__bot)
        await self.__copy.on_load()
        copy_command = self.copy
        copy_command.autocomplete("channel")(self.__copy.channel_name_autocomplete)

        await self.__bot.load_extension("cogs.leveling.impls.info_impl")
        self.__info = Info_Impl(self.__bot)

        await self.__bot.load_extension("cogs.leveling.impls.setup_impl")
        self.__setup = Setup_Impl(self.__bot, self.__configure, self.__copy)
        await self.__setup.on_load()

        return await super().cog_load()
    
    async def cog_unload(self):
        await self.__setup.on_unload()
        await self.__bot.unload_extension("cogs.leveling.impls.setup_impl")

        await self.__bot.unload_extension("cogs.leveling.impls.info_impl")

        await self.__copy.on_unload()
        await self.__bot.unload_extension("cogs.leveling.impls.copy_impl")

        await self.__configure.on_unload()
        await self.__bot.unload_extension("cogs.leveling.impls.configure_impl")

        await self.__bot.unload_extension("cogs.leveling.impls.shared_functions")

        return await super().cog_unload()


async def setup(bot:commands.Bot):
    await bot.add_cog(Leveling_CommandGroup(bot))
