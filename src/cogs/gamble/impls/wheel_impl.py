from discord.ext import commands
import logging
from utils.database.main_controller import Main_DB_Controller
import discord
import random
import math

class Wheel_Impl:
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.gamble.wheel")

    async def on_command(self, ctx: discord.Interaction, bet:int):
        database:Main_DB_Controller = ctx.client.database
        # Check sufficient user balance
        user_balance = await database.get_user_currency(ctx.guild_id, ctx.user.id)
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
                description = "You can bet not less than `10` :dollar:",
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
            await database.add_to_user_balance(ctx.guild_id, ctx.user.id, payout - bet)
        elif payout < bet:
            await database.substract_from_user_balance(ctx.guild_id, ctx.user.id, bet - payout)

async def setup(bot):
    pass