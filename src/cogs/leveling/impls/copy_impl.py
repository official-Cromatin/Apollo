from discord.ext import commands
import discord
from discord import app_commands
import logging
from utils.portal import Portal

class Copy_Impl:
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.leveling.copy")
        self.__portal = Portal.instance()

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

    async def create_message(self, ctx:discord.Interaction):
        # Since there is no other configuration message present, a new one can be created
        await ctx.response.send_message(
            embed = self.get_embed(None, None, None, None),
            view = self.get_view(None, None, None)
        )

        # Create the row in the database to store message settings
        message = await ctx.original_response()
        await self.__portal.database.create_experience_settings_message(ctx.channel_id, ctx.message.id, message.id, None, None, None)

    async def channel_name_autocomplete(self, ctx:discord.Interaction, current:str) -> list[app_commands.Choice]:
        """Autocompletes the channel name based on the configured experience channels"""
        # Request the id of all channels having leveling enabled
        channel_ids = await self.__portal.database.get_leveling_channels(ctx.guild_id)
        choices = []
        counter = 0
        for channel_id in channel_ids:
            # Compare the name of each channel to the current user input
            channel = ctx.guild.get_channel(channel_id)
            if channel.name.lower().startswith(current.lower()):
                choices.append(app_commands.Choice(name = channel.name, value = str(channel_id)))
                counter += 1

            # Limit the amount of options to 25
            if counter == 25:
                break
        return choices

    async def on_command(self, ctx:discord.Interaction, channel:str):
        pass

    async def on_load(self):
        pass

    async def on_unload(self):
        pass


async def setup(bot):
    pass
