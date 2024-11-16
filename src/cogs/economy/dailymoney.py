import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal

class Dailymoney_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.maintenance"))

    @app_commands.command(name = "dailymoney", description = "Pick up your daily salary!")
    async def pickup_dailymoney(self, ctx: discord.Interaction):
        if await self.__portal.database.dailymoney_pickup_ready(ctx.user.id):
            amount = 40
            await ctx.response.send_message(f"You collected your daily salary of `{amount}` :dollar:")
            await self.__portal.database.add_to_user_balance(ctx.user.id, amount)
            await self.__portal.database.reset_pickup_ready(ctx.user.id)
        else:
            await ctx.response.send_message("You have already collected your daily salary")

async def setup(bot: commands.Bot):
    await bot.add_cog(Dailymoney_Command(bot))