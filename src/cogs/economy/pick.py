import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal
import asyncio

class Pick_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.pick"))

    @app_commands.command(name = "pick", description = "Collect appeared or planted money in the current channel")
    async def pick(self, ctx: discord.Interaction):
        # Check for pick message
        result = await self.__portal.database.get_last_pick_message(ctx.channel_id)
        if result is None:
            embed = discord.Embed(
                description = "There is currently no money to collect",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        message_id, amount = result

        # Delete pick message if found
        try:
            pick_message = await ctx.channel.fetch_message(message_id)
            await pick_message.delete()
        except discord.errors.NotFound:
            self._logger.warning("Pick money message was allready deleted!")

        # Create notification for all other mebers
        embed = discord.Embed(
            description = f"<@{ctx.user.id}> has collected {amount} :dollar:"
        )
        await ctx.response.send_message(embed = embed)

        # Credit the user
        await self.__portal.database.add_to_user_balance(ctx.guild_id, ctx.user.id, amount)

        # Wait 5 seconds and delete the notification message
        await asyncio.sleep(5.0)
        await ctx.delete_original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(Pick_Command(bot))