import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_group_cog import Base_GroupCog
from cogs.economy.gamble.impls.betflip_impl import Betflip_Impl
from cogs.economy.gamble.impls.wheel_impl import Wheel_Impl

class Gamble_CommandGroup(Base_GroupCog, group_name='gamble'):
    def __init__(self, bot):
        self.__bot:commands.Bot = bot
        self.__betflip_impl:Betflip_Impl = None
        super().__init__(logging.getLogger("cmds.group"))

    @app_commands.command(name = "wheel", description = "Bets a certain amount of currency on the wheel of fortune")
    @app_commands.describe(bet = "Amount you would like to gamble with")
    async def wheel(self, ctx: discord.Interaction, bet:int):
        await self.__wheel_impl.on_command(ctx, bet)
    
    @app_commands.command(name = "betflip", description = "Bet to guess will the result be heads or tails")
    @app_commands.describe(bet = "Amount you would like to gamble with", guess = "Your guess")
    @app_commands.choices(
        guess = [
            app_commands.Choice(name = "Heads", value = 0),
            app_commands.Choice(name = "Tails", value = 1)
        ]
    )
    async def betflip(self, ctx: discord.Interaction, bet:int, guess:int):
        await self.__betflip_impl.on_command(ctx, bet, guess)

    async def cog_load(self):
        await self.__bot.load_extension("cogs.economy.gamble.impls.wheel_impl")
        await self.__bot.load_extension("cogs.economy.gamble.impls.betflip_impl")
        self.__wheel_impl = Wheel_Impl(self.__bot)
        self.__betflip_impl = Betflip_Impl(self.__bot)

        return await super().cog_load()

    async def cog_unload(self):
        await self.__bot.unload_extension("cogs.economy.gamble.impls.wheel_impl")
        await self.__bot.unload_extension("cogs.economy.gamble.impls.betflip_impl")
        return await super().cog_unload()

async def setup(bot: commands.Bot):
    await bot.add_cog(Gamble_CommandGroup(bot))