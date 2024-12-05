from discord.ext import commands
import logging
from utils.portal import Portal
import discord
import random
import math

class Betroll_Impl:
    def __init__(self, bot:commands.Bot) -> None:
        self.__bot = bot
        self.__logger = logging.getLogger("cmds.gamble.betroll")
        self.__portal = Portal.instance()

    async def on_command(self, ctx:discord.Interaction, bet:int):
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
        
        # Randomize the 10 dice
        dice_emojis = ""
        eye_sum = 0
        for _ in range(10):
            eyes = random.randint(1, 10)
            eye_sum += eyes
            dice_emojis += f":number_{eyes}: "

        if eye_sum <= 66:
            multiplicator = 0
        elif eye_sum > 66 and eye_sum <= 90:
            multiplicator = 2
        elif eye_sum > 90 and eye_sum < 100:
            multiplicator = 4
        else:
            multiplicator = 10
        payout = math.floor(bet * multiplicator)
        
        # Create the embed
        embed = discord.Embed(
            title = "Betroll",
            description = f"The dice have been cast as follows:\n{dice_emojis}"
        )

        embed.add_field(
            name = "Dice eyes sum:",
            value = f"`{eye_sum}`",
            inline = False
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