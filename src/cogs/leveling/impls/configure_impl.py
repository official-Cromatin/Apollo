from discord.ext import commands
import discord
import logging
from utils.database.main_controller import Main_DB_Controller
from utils.interaction_handler.button import Button_Interaction_Handler
from cogs.leveling.impls.shared_functions import Shared_Functions

class Configure_Impl:
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.leveling.configure")
    
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

    async def on_command(self, ctx:discord.Interaction, default_multiplier:float, minimum_threshold:int, maximum_experience:int):
        database:Main_DB_Controller = ctx.client.database
        # Check if there is a configuration presend
        settings = await database.get_experience_settings_message(ctx.channel_id)
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
        await database.set_experience_settings_message(ctx.channel_id, default_multiplier_db, minimum_threshold_db, maximum_experience_db)

        # Edit the original message
        await Shared_Functions.edit_message(
            ctx.channel, message_id, 
            embed = Shared_Functions.get_edit_embed(default_multiplier_db, minimum_threshold_db, maximum_experience_db),
            view = Shared_Functions.get_edit_view(default_multiplier_db, minimum_threshold_db, maximum_experience_db))
    
    async def callback_save(self, ctx:discord.Interaction):
        """Called when a user interacts with the save button of the message"""
        database:Main_DB_Controller = ctx.client.database
        # Load the associated values with the message
        channel_settings:tuple = await database.get_experience_settings_message(ctx.channel_id)
        if channel_settings is None:
            embed = discord.Embed(
                title = "Error while saving",
                description = (
                    "Unfortunately there was a problem with saving.\n"
                    "Please discard the message and open the configuration view again"
                ),
                color = 0xDB3F2F
            )
            ctx.response.send_message(embed = embed, ephemeral = True)
            return
        else:
            default_multiplier, minimum_threshold, maximum_experience, _, original_message_id = channel_settings

        # Save the new values to the database
        await database.set_experience_settings(ctx.guild_id, ctx.channel_id, default_multiplier, minimum_threshold, maximum_experience)
        
        # Cleanup
        await self.callback_discard(ctx)

        # Update main message
        await Shared_Functions.update_main_message(ctx.channel, original_message_id, ctx.channel_id, default_multiplier, minimum_threshold, maximum_experience)

    async def callback_discard(self, ctx:discord.Interaction):
        """Called when a user interacts with the discard button of the message"""
        database:Main_DB_Controller = ctx.client.database
        # Remove the row in the database
        await database.delete_experience_settings_message(ctx.message.id)

        # Delete the message
        await ctx.message.delete()

    async def on_load(self):
        Button_Interaction_Handler.link_button_callback("lvls.conf.save", self)(self.callback_save)
        Button_Interaction_Handler.link_button_callback("lvls.conf.disc", self)(self.callback_discard)

    async def on_unload(self):
        Button_Interaction_Handler.unlink_button_callback("lvls.conf.save")
        Button_Interaction_Handler.unlink_button_callback("lvls.conf.disc")


async def setup(bot):
    pass
