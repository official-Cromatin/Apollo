from discord.ext import commands
import discord
from discord import app_commands
import logging
from utils.database.main_controller import Main_DB_Controller
from cogs.leveling.impls.shared_functions import Shared_Functions

class Copy_Impl:
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.leveling.copy")

    def get_embed(self, default_multiplier:float, minimum_threshold:int, maximum_experience:int, channel_name:str = None) -> discord.Embed:
        """Creates and returns the embed, embedding the provided values"""
        if channel_name is None:
            channel_name = "None selected"

        embed = discord.Embed(
            title = "Copy the configuration from another channel",
            description = (
                f"**__Configuration for the channel:__ `{channel_name}`**\n"
                f"- Multiplier, being multiplied by the length of the message: `{default_multiplier}`\n"
                f"- Threshold above which the user is rewarded: `{minimum_threshold}`\n"
                f"- Limit for the maximum amount of receivable experience: `{maximum_experience}`\n"
                "-# Important: The amount of gained experience is calculated by multiplying the message length by the multiplier"
            )
        )
        embed.set_footer(text = "Use the '/leveling copy' command to select a channel to copy the values from")
        return embed
    
    def get_view(self, default_multiplier:float, minimum_threshold:int, maximum_experience:int) -> discord.ui.View:
        """Returns the view, depending on the provided values, the "Save" Button will be disabled until all values are not None"""
        save_disabled = any(value is None for value in [default_multiplier, minimum_threshold, maximum_experience])
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label = "Save", custom_id = "lvls.conf.save", style = discord.ButtonStyle.green, disabled = save_disabled))
        view.add_item(discord.ui.Button(label = "Discard", custom_id = "lvls.conf.disc", style = discord.ButtonStyle.red))
        return view

    async def channel_name_autocomplete(self, ctx:discord.Interaction, current:str) -> list[app_commands.Choice]:
        """Autocompletes the channel name based on the configured experience channels"""
        database:Main_DB_Controller = ctx.client.database
        # Request the id of all channels having leveling enabled
        channel_ids = await database.get_leveling_channels(ctx.guild_id)
        choices = []
        counter = 0
        for channel_id in channel_ids:
            # Check if the channel exists, if not, continue with the next
            channel = ctx.guild.get_channel(channel_id)
            if channel is None:
                continue

            # Compare the name of each channel to the current user input
            if channel.name.lower().startswith(current.lower()):
                choices.append(app_commands.Choice(name = channel.name, value = str(channel_id)))
                counter += 1

            # Limit the amount of options to 25
            if counter == 25:
                break
        return choices

    async def on_command(self, ctx:discord.Interaction, channel:str):
        database:Main_DB_Controller = ctx.client.database
        # Check if the input is numeric
        if not channel.isnumeric():
            embed = discord.Embed(
                title = "Incorrect input",
                description = "The input must be a selection from the available options, given by the command",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        
        # Check if the given channel_id matches to any present channels
        channel_ids = await database.get_leveling_channels(ctx.guild_id)
        selected_channel_id = int(channel)
        if not selected_channel_id in channel_ids:
            embed = discord.Embed(
                title = "Non existing channel",
                description = (
                    "The specified channel does not exist on this Guild.\n"
                    "In addition, the entry of arbitrary numbers is not permitted"
                ),
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        
        # Check if there is a configuration message present in the current channel
        channel_settings = await database.get_experience_settings_message(ctx.channel_id)
        if channel_settings is None:
            embed = discord.Embed(
                description = (
                    "This command only works in the same channel in which a configuration message exists\n"
                    "Use the '/leveling setup' command to open the overview and then click on the 'Configure channel' button"
                ),
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        
        # Copy the settings from the provided one and apply them to this channel
        default_multiplier, minimum_threshold, maximum_experience = await database.get_experience_settings(selected_channel_id)
        await database.set_experience_settings_message(ctx.channel_id, default_multiplier, minimum_threshold, maximum_experience)

        # Update the configuration message
        await Shared_Functions.update_edit_message(ctx.channel, channel_settings[3], default_multiplier, minimum_threshold, maximum_experience)

        # Confirm the action
        embed = discord.Embed(
            title = "Settings loaded successfully",
            description = f"The settings of the <#{selected_channel_id}> channel have been loaded successfully, don't forget to save them :)",
            color = 0x4BB543
        )
        await ctx.response.send_message(embed = embed, ephemeral = True)

    async def on_load(self):
        pass

    async def on_unload(self):
        pass


async def setup(bot):
    pass
