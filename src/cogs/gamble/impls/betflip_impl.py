from discord.ext import commands
import logging
from utils.database.main_controller import Main_DB_Controller
import discord
import random
import math

class Betflip_Impl:
    def __init__(self, bot:commands.Bot) -> None:
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.gamble.betflip")
        
    # Handler method for the on_command event
    async def on_command(self, ctx: discord.Interaction, bet:int, guess:int):
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
        ctx.user.name
        
        # Check if bet is greater than 10 dollar
        if bet < 2:
            embed = discord.Embed(
                description = "You can bet not less than `2` :dollar:",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed)
            return
        
        # Randomize the upper side of the coin
        coin_upper = random.randint(0, 1)
        if coin_upper == guess:
            multiplicator = 1.95
        else:
            multiplicator = 0
        payout = math.floor(bet * multiplicator)

        # Create the embed
        embed = discord.Embed(title = "Betflip")
        embed.add_field(
            name = "Your guess:",
            value = "Head" if guess == 0 else "Tails"
        )
        embed.add_field(
            name = "Outcome:",
            value = "Head" if coin_upper == 0 else "Tails"
        )
        embed.add_field(
            name = "\u200b",
            value = "\u200b"
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

        # Change the users balance
        if payout > bet:
            await database.add_to_user_balance(ctx.guild_id, ctx.user.id, payout - bet)
        elif payout < bet:
            await database.substract_from_user_balance(ctx.guild_id, ctx.user.id, bet - payout)

async def setup(bot):
    pass