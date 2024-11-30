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
        super().__init__(logging.getLogger("cmds.dailymoney"))

    @app_commands.command(name = "dailymoney", description = "Pick up your daily salary!")
    async def pickup_dailymoney(self, ctx: discord.Interaction):
        if await self.__portal.database.dailymoney_pickup_ready(ctx.user.id):
            # Get the ids of user roles
            user_role_ids = []
            for role in ctx.user.roles[1:]:
                user_role_ids.append(role.id)

            # Determine the daily salary
            daily_salary = await self.__portal.database.get_daily_salary(ctx.guild_id, user_role_ids)

            if daily_salary is None:
                await ctx.response.send_message("You do not own any roles that are registered for Dailymoney")
                return

            await ctx.response.send_message(f"You collected your daily salary of `{daily_salary}` :dollar:")
            await self.__portal.database.add_to_user_balance(ctx.guild_id, ctx.user.id, daily_salary)
            await self.__portal.database.reset_pickup_ready(ctx.user.id)
        else:
            await ctx.response.send_message("You have already collected your daily salary")

async def setup(bot: commands.Bot):
    await bot.add_cog(Dailymoney_Command(bot))