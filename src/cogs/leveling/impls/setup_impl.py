from discord.ext import commands
import discord
import logging
from utils.portal import Portal
from tabulate import tabulate
from utils.interaction_handler.button import Button_Interaction_Handler

class Setup_Impl:
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.leveling.setup")
        self.__portal = Portal.instance()

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

        # Create embed to display the settings
        table_content = tabulate(
            [
                ("Multiplier:", default_multiplier),
                ("Lower limit:", minimum_threshold),
                ("Upper limit:", maximum_experience)
            ],
            tablefmt = "rounded_outline"
        )
        embed = discord.Embed(
            title = f"Configuration for obtaining experience in <#{ctx.channel_id}> channel",
            description = f"```{table_content}```"
        )
        await ctx.response.send_message(embed = embed, view = self.get_view())


async def setup(bot):
    pass