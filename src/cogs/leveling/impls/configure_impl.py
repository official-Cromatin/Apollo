from discord.ext import commands
import discord
import logging
from utils.portal import Portal

class Configure_Impl:
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.leveling.configure")
        self.__portal = Portal.instance()

    def get_embed(self, default_multiplier:float, minimum_threshold:int, maximum_experience:int) -> discord.Embed:
        embed = discord.Embed(
            title = "Editing the configuration",
            description = (
                "**__Configuration for this channel:__**\n"
                f"- Multiplier, being multiplied by the length of the message: `{default_multiplier}`\n"
                f"- Threshold above which the user is rewarded: `{minimum_threshold}`\n"
                f"- Limit for the maximum amount of receivable experience: `{maximum_experience}`\n"
                "-# Important: The amount of gained experience is calculated by multiplying the message length by the multiplier"
            )
        )
        embed.set_footer(text = "Use the '/leveling configure' command to edit the values")
        return embed

    async def on_command(self, ctx:discord.Interaction):
        pass

    async def create_message(self, ctx:discord.Interaction):
        # Load settings for channel (if existing)
        channel_settings:tuple = await self.__portal.database.get_experience_settings(ctx.channel_id)
        if channel_settings is None:
            default_multiplier = minimum_threshold = maximum_experience = None
        else:
            default_multiplier, minimum_threshold, maximum_experience = channel_settings

        # Create the embed
        await ctx.response.send_message(embed = self.get_embed(default_multiplier, minimum_threshold, maximum_experience))

        # Create the row in the database to store message settings
        message = await ctx.original_response()
        await self.__portal.database.create_experience_settings_message(ctx.message.id, message.id, default_multiplier, minimum_threshold, maximum_experience)
    
    async def on_load(self):
        pass

    async def on_unload(self):
        pass


async def setup(bot):
    pass
