import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal
import aiofiles
from pathlib import Path

class Plant_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.plant"))

    @app_commands.command(name = "plant", description = "Plant a certain amount of your balance in the current channel")
    @app_commands.describe(amount = "Amount of money to be planted in the current channel")
    async def plant(self, ctx: discord.Interaction, amount:int):
        # Check for great enougth amount
        if amount <= 0:
            embed = discord.Embed(
                description = "You cannot plant less than `1` :dollar:",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return

        # Check for sufficient balance of user
        user_balance = await self.__portal.database.get_user_currency(ctx.guild_id, ctx.user.id)
        if amount > user_balance:
            embed = discord.Embed(
                description = f"You try to plant `{amount}` :dollar:, but only have `{user_balance}` :dollar:",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        
        # Create and send the plant message
        file_path = Path(self.__portal.source_path) / "assets" / "img1.jpg"
        attatchment_image = discord.File(file_path)
        await ctx.response.send_message(
            content = f"<@{ctx.user.id}> planted `{amount}` :dollar:, collect them by typing `/pick`, quick!",
            file = attatchment_image
        )

        # Substract from users balance and create db entry
        message = await ctx.original_response()
        await self.__portal.database.substract_from_user_balance(ctx.guild_id, ctx.user.id, amount)
        await self.__portal.database.create_pick_message(ctx.guild_id, ctx.channel_id, message.id, amount)


async def setup(bot: commands.Bot):
    await bot.add_cog(Plant_Command(bot))