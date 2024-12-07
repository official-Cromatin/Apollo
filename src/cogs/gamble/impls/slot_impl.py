from discord.ext import commands
import logging
from utils.portal import Portal
import discord
import random
import math

class Slot_Impl:
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.gamble.slot")
        self.__portal = Portal.instance()

    async def on_command(self, ctx:discord.Interaction, bet:int):
        EMOJIS = [":butterfly:", ":heart:", ":dolphin:", ":sun_with_face:", ":green_apple:", ":cherry_blossom:"]
        MAX_VALUE = len(EMOJIS) - 1

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
                description = "You can bet not less than `10` :dollar:",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed)
            return
        
        # Randomize the symbols
        slot_emojis = ""
        slot_positions = []
        for _ in range(3):
            position = random.randint(0, MAX_VALUE)
            slot_positions.append(position)
            slot_emojis += f"{EMOJIS[position]} "

        if all(n == MAX_VALUE for n in slot_positions):
            multiplicator = 30  # Three flowers
        elif all(n == slot_positions[0] for n in slot_positions):
            multiplicator = 10  # Three same
        elif sum(1 for n in slot_positions if n == MAX_VALUE) == 2:
            multiplicator = 4  # Two flowers
        elif any(n == MAX_VALUE for n in slot_positions):
            multiplicator = 1  # One flowers
        else:
            multiplicator = 0  # No payout
        payout = math.floor(bet * multiplicator)

        # Create the embed
        embed = discord.Embed(
            title = "Slots",
            description = f"The rollers have come to a standstill at the following points:\n{slot_emojis}"
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

async def setup(bot):
    pass