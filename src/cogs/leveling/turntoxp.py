import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal
from utils.calc_lvl_xp import calculate_current_level_experience

class TurnToXP_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.turntoxp"))

    @app_commands.command(name = "turntoxp", description = "Converts a certain amount of balance to xp")
    @app_commands.describe(amount = "Amount of money to be converted, each dollar equals to 5 xp")
    async def command_name(self, ctx:discord.Interaction, amount:int):
        # Check sufficient balance
        user_balance = await self.__portal.database.get_user_currency(ctx.guild_id, ctx.user.id)
        if user_balance is None:
            embed = discord.Embed(
                description = "You do not have an account balance yet\nCollect your dailymoney or get gifted some",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        if user_balance < amount:
            embed = discord.Embed(
                description = "Your balance is not sufficient",
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        
        # Substract from user balance
        await self.__portal.database.substract_from_user_balance(ctx.guild_id, ctx.user.id, amount)

        # Convert to xp
        gained_xp = amount * 5
        leveled_up, user_lvl, user_xp = await self.__portal.database.add_to_user_experience(ctx.guild_id, ctx.user.id, gained_xp)
        
        # Create and send embed
        embed_description = f"You have successfully converted `{amount}` :dollar: to `{gained_xp}` XP"
        if leveled_up:
            embed_description += f"\nCongratulations, you have reached level `{user_lvl}`, `{calculate_current_level_experience(user_lvl)}` XP to go till the next level"
        else:
            embed_description += f"\nUntil you reach the next level, you still have to gain `{calculate_current_level_experience(user_lvl) - user_xp}` XP"
        embed = discord.Embed(
            description = embed_description
        )
        await ctx.response.send_message(embed = embed)
        

async def setup(bot: commands.Bot):
    await bot.add_cog(TurnToXP_Command(bot))
