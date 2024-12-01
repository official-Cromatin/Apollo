import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal
import random
import math

class Wheel_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.wheel"))

    @app_commands.command(name = "wheel", description = "Bets a certain amount of currency on the wheel of fortune")
    @app_commands.describe(bet = "Amount you would like to gamble with")
    async def wheel(self, ctx: discord.Interaction, bet:int):
        # Check sufficient user balance
        user_balance = await self.__portal.database.get_user_currency(ctx.guild_id, ctx.user.id)
        if user_balance is None:
            embed = discord.Embed(
                description = "You do not have an account balance yet\nCollect your dailymoney or get gifted some",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed)
            return
        if user_balance < bet:
            embed = discord.Embed(
                description = (
                    "Your credit is not sufficient\n"
                    f"You are trying to gamble with `{bet}` :dollar:, but you only have `{user_balance}` :dollar:"
                ),
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed)
            return
        
        # Check if bet is greater than 10 dollar
        if bet < 10:
            embed = discord.Embed(
                description = "You can bet no less than `10` :dollar:",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed)
            return

        # Randomize the position of the wheel and its multiplicator
        match random.randint(0, 7):
            case 0:
                arrow = "↑"
                multiplicator = 1.7
            case 1:
                arrow = "↗"
                multiplicator = 2.4
            case 2:
                arrow = "→"
                multiplicator = 1.2
            case 3:
                arrow = "↘"
                multiplicator = 0.5
            case 4:
                arrow = "↓"
                multiplicator = 0.3
            case 5:
                arrow = "↙"
                multiplicator = 0.1
            case 6:
                arrow = "←"
                multiplicator = 0.2
            case 7:
                arrow = "↖"
                multiplicator = 1.5
        payout = math.floor(bet * multiplicator)

        # Create the embed
        embed = discord.Embed(
            title = "Wheel of Fortune",
            description = (
                "```"
                "『1.5』 『1.7』 『2.4』\n\n"
                f"『0.2』   {arrow}    『1.2』\n\n"
                "『0.1』 『0.3』 『0.5』"
                "```"
            )
        )
        embed.add_field(
            name = "Bet:",
            value = f"`{bet}` :dollar:"
        )
        embed.add_field(
            name = "Multiplier:",
            value = f"`{multiplicator}`"
        )
        embed.add_field(
            name = "Payout:",
            value = f"`{payout}` :dollar:"
        )
        await ctx.response.send_message(embed = embed)

        # Change the user's balance
        if payout == bet:
            pass
        elif payout > bet:
            await self.__portal.database.add_to_user_balance(ctx.guild_id, ctx.user.id, payout - bet)
        elif payout < bet:
            await self.__portal.database.substract_from_user_balance(ctx.guild_id, ctx.user.id, bet - payout)

async def setup(bot: commands.Bot):
    await bot.add_cog(Wheel_Command(bot))