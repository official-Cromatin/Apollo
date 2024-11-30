import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal

class Give_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.give"))

    @app_commands.command(name = "give", description = "Transfer part of your balance to another user")
    @app_commands.describe(member = "User you want to give money to")
    @app_commands.describe(amount = "Amount of balance you want to gift")
    async def give(self, ctx: discord.Interaction, member: discord.Member, amount: int):
        # Get balance of current user
        user_balance = await self.__portal.database.get_user_currency(ctx.guild_id, ctx.user.id)
        
        # Check for sufficient balance
        if user_balance is None:
            embed = discord.Embed(
                description = "You do not have an account balance yet\nCollect your dailymoney or get gifted some",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed)
            return
        if user_balance < amount:
            embed = discord.Embed(
                description = (
                    "Your credit is not sufficient\n"
                    f"You are trying to give away `{amount}` :dollar: to <@{member.id}>, but you only have `{user_balance}` :dollar:"
                ),
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed)
            return
        
        # Check if source and target user are the same
        if ctx.user.id == member.id:
            embed = discord.Embed(
                description = "You cannot transfer money to yourself!",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed)
            return
        
        # Transfer the money to another user
        await self.__portal.database.substract_from_user_balance(ctx.guild_id, ctx.user.id, amount)
        await self.__portal.database.add_to_user_balance(ctx.guild_id, member.id, amount)

        embed = discord.Embed(
            description = (
                f"Successfully transferred `{amount}` :dollar: to <@{member.id}>\n"
                f"Your remaining balance is `{user_balance - amount}` :dollar:"
            ),
            color = 0x4BB543
        )
        await ctx.response.send_message(embed = embed)
            

async def setup(bot: commands.Bot):
    await bot.add_cog(Give_Command(bot))