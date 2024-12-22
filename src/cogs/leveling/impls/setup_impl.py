from discord.ext import commands
import discord
import logging
from utils.portal import Portal
from tabulate import tabulate
from utils.interaction_handler.button import Button_Interaction_Handler
from cogs.leveling.impls.configure_impl import Configure_Impl
from cogs.leveling.impls.copy_impl import Copy_Impl
from cogs.leveling.impls.shared_functions import Shared_Functions

class Setup_Impl:
    def __init__(self, bot:commands.Bot, configure:Configure_Impl, copy:Copy_Impl):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.leveling.setup")
        self.__portal = Portal.instance()

        self.__configure = configure
        self.__copy = copy

    async def on_command(self, ctx:discord.Interaction):
        # Load channel settings
        channel_settings:tuple = await self.__portal.database.get_experience_settings(ctx.channel_id)
        if channel_settings is None:
            embed = discord.Embed(
                title = f"Configuration for obtaining experience in <#{ctx.channel_id}> channel",
                description = "```No configuration found```"
            )
            await ctx.response.send_message(embed = embed, view = self.get_view())
            return
        default_multiplier, minimum_threshold, maximum_experience = channel_settings

        embed = Shared_Functions.get_main_embed(ctx.channel_id, default_multiplier, minimum_threshold, maximum_experience)
        view = Shared_Functions.get_main_view()
        await ctx.response.send_message(embed = embed, view = view)

    async def callback_conf(self, ctx:discord.Interaction):
        """Called when a user interacts with the "Configure channel" button of the main view"""
        await self.__configure.create_message(ctx)

    async def callback_copy(self, ctx:discord.Interaction):
        """Called when a user interacts with the "Copy settings from channel" button of the main view"""
        await self.__copy.create_message(ctx)

    async def on_load(self):
        Button_Interaction_Handler.link_button_callback("lvls.main.conf", self)(self.callback_conf)
        Button_Interaction_Handler.link_button_callback("lvls.main.copy", self)(self.callback_copy)

    async def on_unload(self):
        Button_Interaction_Handler.unlink_button_callback("lvls.main.conf")
        Button_Interaction_Handler.unlink_button_callback("lvls.main.copy")


async def setup(bot):
    pass