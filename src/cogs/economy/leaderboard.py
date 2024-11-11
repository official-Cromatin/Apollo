import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
import math
from utils.portal import Portal
from utils.database.main_controller import Main_DB_Controller

class Leaderboard_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot:commands.Bot = bot
        self.__portal:Portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.maintenance"))

    async def get_number_of_leaderboard_pages(self, guild_id:int, page_size:int = 9) -> int:
        """Returns the number of pages that can be displayed for an leaderboard, for an certain guild"""
        return math.ceil(await self.__portal.database.get_number_of_users(guild_id) / page_size)

    @app_commands.command(name = "leaderboard", description = "Displays the leaderboard, for the users with the most currency on the server")
    @app_commands.describe(current_page = "Display an certain page of the leaderboard")
    async def show_leaderboard(self, ctx: discord.Interaction, current_page:int = 0):
        no_of_pages = await self.get_number_of_leaderboard_pages(ctx.guild_id)

        if current_page > no_of_pages:
            embed = discord.Embed(
                description = f"The last page is `{no_of_pages}`",
                color = 0xDB3F2F)
            await ctx.response.send_message(embed = embed)
            return

        await ctx.response.defer()
        if current_page < 1:
            current_page_offset = 0
        else:
            current_page_offset = current_page - 1
        placement = current_page_offset * 9
        
        embed = discord.Embed(
            title = "Leaderbaord :dollar:",
            color = 0x4184BC)
        users = await self.__portal.database.get_leaderboard_page_users(ctx.guild_id, current_page_offset * 9)
        for user in users:
            discord_user = await self.__bot.fetch_user(user['user_id'])
            embed.add_field(
                name = f"#{placement + 1} {discord_user.name}",
                value = f"`{user['balance']}` :dollar:",
                inline = True
            )
            placement += 1

        embed.set_footer(text = f"{current_page_offset + 1} / {no_of_pages}")

        await ctx.followup.send(embed = embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard_Command(bot))