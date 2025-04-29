import logging
from cogs.base_cog import Base_Cog
import discord
from discord import app_commands
from discord.ext import commands
from utils.database.main_controller import Main_DB_Controller
import traceback

class Currency_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot = bot
        super().__init__(logging.getLogger("cmds.currency"))

    @app_commands.command(name = "currency", description = "Displays your own or someone else's account balance")
    @app_commands.describe(member = "Displays balance for the selected user")
    async def currency(self, ctx: discord.Interaction, member: discord.Member = None):
        database:Main_DB_Controller = ctx.client.database
        try:
            if member:
                currency = await database.get_user_currency(ctx.guild_id, member.id)
                print("Selected member", ctx.guild_id, member.id)
                if currency is None:
                    embed = discord.Embed(
                        description = f"The user does not have an account balance",
                        color = 0xDB3F2F
                    )
                else:
                    embed = discord.Embed(
                        description = f"His account balance is {currency} :dollar:",
                        color = 0x4184BC
                    )
            else:
                currency = await database.get_user_currency(ctx.guild_id, ctx.user.id)
                print("Own currency", ctx.guild_id, ctx.user.id)
                if currency is None:
                    embed = discord.Embed(
                        description = "You do not have an account balance yet\nCollect your dailymoney or get gifted some",
                        color = 0xDB3F2F
                    )
                else:
                    embed = discord.Embed(
                        description = f"Your current balance `{currency}` :dollar:",
                        color = 0x4184BC
                    )

            await ctx.response.send_message(embed = embed)
        except Exception as error:
            traceback.print_exception(type(error), error, error.__traceback__)

async def setup(bot: commands.Bot):
    await bot.add_cog(Currency_Command(bot))