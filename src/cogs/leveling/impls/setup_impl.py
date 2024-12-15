from discord.ext import commands
import discord
import logging
from utils.portal import Portal
from tabulate import tabulate
from utils.interaction_handler.button import Button_Interaction_Handler
from cogs.leveling.impls.configure_impl import Configure_Impl

class Setup_Impl:
    def __init__(self, bot:commands.Bot, configure:Configure_Impl):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.leveling.setup")
        self.__portal = Portal.instance()

        self.__configure = configure

    def get_view(self) -> discord.ui.View:
        """Returns the view for the main view"""
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label = "Configure channel", style = discord.ButtonStyle.blurple, custom_id = "lvls.main.conf"))
        view.add_item(discord.ui.Button(label = "Copy settings from channel", style = discord.ButtonStyle.blurple, custom_id = "lvls.main.copy"))
        return view

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

        embed = discord.Embed(
            title = f"Current configuration for obtaining experience in <#{ctx.channel_id}> channel",
            description = (
                "**__Configuration for this channel:__**\n"
                f"- Multiplier, being multiplied by the length of the message: `{default_multiplier}`\n"
                f"- Threshold above which the user is rewarded: `{minimum_threshold}`\n"
                f"- Limit for the maximum amount of receivable experience: `{maximum_experience}`\n"
                "-# Important: The amount of gained experience is calculated by multiplying the message length by the multiplier"
            )
        )
        await ctx.response.send_message(embed = embed, view = self.get_view())

    async def callback_conf(self, ctx:discord.Interaction):
        """Called when a user interacts with the "Configure channel" button of the main view"""
        await self.__configure.create_message(ctx)


    async def on_load(self):
        Button_Interaction_Handler.link_button_callback("lvls.main.conf", self)(self.callback_conf)

    async def on_unload(self):
        Button_Interaction_Handler.unlink_button_callback("lvls.main.conf")

async def setup(bot):
    pass