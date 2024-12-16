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
        """Creates and returns the embed, embedding the provided values"""
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
    
    @staticmethod
    def return_biggest(*values:int | None, default:int = None) -> int | None:
        """Returns the biggest value from the provided ones"""
        filtered_values = [v for v in values if v is not None]
        return max(filtered_values, default = default)
    
    @staticmethod
    def return_smallest(*values:int | None, default:int = None) -> int | None:
        """Returns the smallest value from the provided ones"""
        filtered_values = [v for v in values if v is not None]
        return min(filtered_values, default = default)
    
    async def edit_message(self, channel:discord.TextChannel, message_id:int, embed:discord.Embed = ..., view:discord.ui.View = ...) -> discord.Message:
        """Edits the embed and view of the message in the provided channel, returns the edited message"""
        message = await channel.fetch_message(message_id)

        # Check which values are provided
        kwargs = {}
        if embed is not ...:
            kwargs['embed'] = embed
        if view is not ...:
            kwargs['view'] = view
        return await message.edit(**kwargs)

    async def on_command(self, ctx:discord.Interaction, default_multiplier:float, minimum_threshold:int, maximum_experience:int):
        # Check if there is a configuration presend
        settings = await self.__portal.database.get_experience_settings_message(ctx.channel_id)
        if settings is None:
            embed = discord.Embed(
                description = (
                    "This command only works in the same channel in which a configuration message exists\n"
                    "Use the '/leveling setup' command to open the overview and then click on the 'Configure channel' button"
                ),
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        default_multiplier_db, minimum_threshold_db, maximum_experience_db, message_id, _ = settings

        # Check if all values are none
        if default_multiplier is None and minimum_threshold is None and maximum_experience is None:
            embed = discord.Embed(
                description = "You must change at least one attribute",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        
        # Check wich attributes have changed
        default_multiplier_string = ""
        minimum_threshold_string = ""
        maximum_experience_string = ""
        if default_multiplier is not None:
            if default_multiplier <= 0.0 or default_multiplier > 512.0:
                embed = discord.Embed(
                    title = "Error during processing",
                    description = "The multiplier must be greater than 0 and less than 512",
                    color = 0xDB3F2F
                )
                await ctx.response.send_message(embed = embed, ephemeral = True)
                return
            else:
                default_multiplier_string = f"- Default multiplier changed from `{default_multiplier_db}` to `{default_multiplier}`\n"
                default_multiplier_db = default_multiplier
        if minimum_threshold is not None:
            if minimum_threshold < 0 or minimum_threshold >= self.return_biggest(maximum_experience, maximum_experience_db):
                embed = discord.Embed(
                    title = "Error during processing",
                    description = "The minimum treashold value must be LESS than the maximum amount of experience obtainable, while being greater than `0`",
                    color = 0xDB3F2F
                )
                await ctx.response.send_message(embed = embed, ephemeral = True)
                return
            else:
                minimum_threshold_string = f"- Minimum treashold changed from `{minimum_threshold_db}` to `{minimum_threshold}`\n"
                minimum_threshold_db = minimum_threshold
                print("ABC")
        if maximum_experience is not None:
            if maximum_experience <= self.return_smallest(minimum_threshold, minimum_threshold_db):
                embed = discord.Embed(
                    title = "Error during processing",
                    description = "The amount of maximum obtainable experience muss be MORE than the lowest amount of obtainable experience",
                    color = 0xDB3F2F
                )
                await ctx.response.send_message(embed = embed, ephemeral = True)
                return
            else:
                maximum_experience_string = f"- Maximum experience changed from `{maximum_experience_db}` to `{maximum_experience}`\n"
                maximum_experience_db = maximum_experience

        # Create the success message
        embed = discord.Embed(
            title = "Successfully edited the parameters",
            description = default_multiplier_string + minimum_threshold_string + maximum_experience_string,
            color = 0x4BB543
        )
        await ctx.response.send_message(embed = embed, ephemeral = True)

        # Edit the values in the database
        await self.__portal.database.set_experience_settings_message(ctx.channel_id, default_multiplier_db, minimum_threshold_db, maximum_experience_db)

        # Edit the original message
        await self.edit_message(ctx.channel, message_id, embed = self.get_embed(default_multiplier_db, minimum_threshold_db, maximum_experience_db))

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
