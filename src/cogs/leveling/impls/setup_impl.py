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
            await ctx.response.send_message(embed = embed, view = Shared_Functions.get_main_view())
            return
        default_multiplier, minimum_threshold, maximum_experience = channel_settings

        embed = Shared_Functions.get_main_embed(ctx.channel_id, default_multiplier, minimum_threshold, maximum_experience)
        view = Shared_Functions.get_main_view()
        await ctx.response.send_message(embed = embed, view = view)

    async def callback_edit(self, ctx:discord.Interaction):
        """Called when a user interacts with the "Edit configuration" button of the main view"""
        # Since there is no other configuration message present, the requested view can be created
        settings = await self.__portal.database.get_experience_settings(ctx.channel_id)
        if settings is None:
            default_multiplier = minimum_threshold = maximum_experience = None
        else:
            default_multiplier, minimum_threshold, maximum_experience = settings

        await ctx.response.send_message(
            embed = Shared_Functions.get_edit_embed(default_multiplier, minimum_threshold, maximum_experience),
            view = Shared_Functions.get_edit_view(default_multiplier, minimum_threshold, maximum_experience)
        )

        # Create the row in the database to store message settings
        message = await ctx.original_response()
        await self.__portal.database.create_experience_settings_message(ctx.channel_id, ctx.message.id, message.id, default_multiplier, minimum_threshold, maximum_experience)

    async def on_load(self):
        Button_Interaction_Handler.link_button_callback("lvls.main.edit", self)(self.callback_edit)

    async def on_unload(self):
        Button_Interaction_Handler.unlink_button_callback("lvls.main.edit")


async def setup(bot):
    pass