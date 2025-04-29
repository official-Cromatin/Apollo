from discord.ext import commands
import discord
import logging
from utils.database.main_controller import Main_DB_Controller
import math

class Info_Impl:
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.leveling.configure")

    async def on_command(self, ctx:discord.Interaction, channel:discord.TextChannel | None):
        database:Main_DB_Controller = ctx.client.database
        if channel is None:
            channel = ctx.channel

        # Check if the selected channel is a leveling channel
        channel_ids = await database.get_leveling_channels(ctx.guild_id)
        if not channel.id in channel_ids:
            embed = discord.Embed(
                title = f"Information about the channel: {channel.name}",
                description = "This channel is not unlocked to receive XP"
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return

        # Get the information for the specified channel
        default_multiplier, minimum_threshold, maximum_experience = await database.get_experience_settings(channel.id)

        # Create and send the embed
        embed = discord.Embed(
            title = f"Information about the channel: {channel.name}",
            description = (
                f"- Multiplier, being multiplied by the length of the message: `{default_multiplier}`\n"
                f"- Threshold above which the user is rewarded: `{minimum_threshold}`\n"
                f"- Limit for the maximum amount of receivable experience: `{maximum_experience}`\n"
                f"From a message length of `{math.ceil(minimum_threshold / default_multiplier)}` characters you get xp, each character is multiplied by `{default_multiplier}` and you can get a maximum of `{maximum_experience}` xp per message\n\n"
                "Calculation formula for this channel:\n"
                f"```xp = message_length * {default_multiplier}```"
            )
        )
        await ctx.response.send_message(embed = embed, ephemeral = True)


async def setup(bot):
    pass