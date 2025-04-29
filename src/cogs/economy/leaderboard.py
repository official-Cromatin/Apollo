import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
import math
from utils.database.main_controller import Main_DB_Controller
from utils.interaction_handler.button import Button_Interaction_Handler

from datetime import datetime
from utils.datetime_tools import get_elapsed_time_milliseconds

class Leaderboard_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot:commands.Bot = bot
        super().__init__(logging.getLogger("cmds.maintenance"))

    async def get_number_of_leaderboard_pages(self, guild_id:int, page_size:int = 9) -> int:
        """Returns the number of pages that can be displayed for an leaderboard, for an certain guild"""
        database:Main_DB_Controller = self.__bot.database
        return math.ceil(await database.get_number_of_users(guild_id) / page_size)
    
    async def get_next_page(self, message_id:int, increment:bool = True) -> int:
        """Returns the true (first page is `0`) id of the next page
        
        When `increment` is `False`, it will be counted downwards, but never below zero"""
        database:Main_DB_Controller = self.__bot.database
        current_page = await database.get_leaderboard_page(message_id)
        if increment:
            current_page = current_page + 1
        else:
            current_page = current_page - 1
            if current_page < 0:
                current_page = 0

        return current_page
    
    def create_button_view(self, current_page:int, number_of_pages:int) -> discord.ui.View:
        """Creates a new view with two buttons to interact with the current view"""
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Previous", custom_id = "econ.lb.prev", disabled = True if current_page == 0 else False))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Next", custom_id = "econ.lb.next", disabled = True if current_page == number_of_pages else False))
        return view
    
    async def create_embed(self, guild_id:int, current_page:int, number_of_pages:int) -> discord.Embed:
        """Create a new embed, to display the users on the current page aswell as thier currency"""
        database:Main_DB_Controller = self.__bot.database
        users = await database.get_leaderboard_page_users(guild_id, current_page * 9)
        placement = current_page * 9

        embed = discord.Embed(
            title = "Leaderbaord :dollar:",
            color = 0x4184BC)
        for user in users:
            begin = datetime.now().timestamp()
            discord_user = await self.__bot.hybrid_get_user(user['user_id'])
            print(get_elapsed_time_milliseconds(datetime.now().timestamp() - begin))
            embed.add_field(
                name = f"#{placement + 1} {discord_user.name}",
                value = f"`{user['balance']}` :dollar:",
                inline = True
            )
            placement += 1
        embed.set_footer(text = f"{current_page + 1} / {number_of_pages}")

        return embed

    @app_commands.command(name = "leaderboard", description = "Displays the leaderboard, for the users with the most currency on the server")
    @app_commands.describe(current_page = "Display an certain page of the leaderboard")
    async def show_leaderboard(self, ctx: discord.Interaction, current_page:int = 0):
        database:Main_DB_Controller = self.__bot.database
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
        
        embed = await self.create_embed(ctx.guild_id, current_page_offset, no_of_pages)
        await ctx.followup.send(embed = embed, view = self.create_button_view(current_page_offset, no_of_pages))
        
        message = await ctx.original_response()
        await database.create_leaderboard_page(message.id, current_page_offset)

    #@Button_Interaction_Handler.link_button_callback("econ.lb.prev")
    async def previous_button_callback(self, ctx: discord.Interaction):
        database:Main_DB_Controller = self.__bot.database

        current_page = await self.get_next_page(ctx.message.id, False)
        no_of_pages = await self.get_number_of_leaderboard_pages(ctx.guild_id)

        embed = await self.create_embed(ctx.guild_id, current_page, no_of_pages)
        await ctx.response.edit_message(embed = embed, view = self.create_button_view(current_page, no_of_pages))
        await database.update_leaderboard_page(ctx.message.id, current_page)

    #@Button_Interaction_Handler.link_button_callback("econ.lb.next")
    async def next_button_callback(self, ctx: discord.Interaction):
        database:Main_DB_Controller = self.__bot.database

        current_page = await self.get_next_page(ctx.message.id, True)
        no_of_pages = await self.get_number_of_leaderboard_pages(ctx.guild_id)

        embed = await self.create_embed(ctx.guild_id, current_page, no_of_pages)
        await ctx.response.edit_message(embed = embed, view = self.create_button_view(current_page + 1, no_of_pages))
        await database.update_leaderboard_page(ctx.message.id, current_page)

    async def cog_load(self):
        Button_Interaction_Handler.link_button_callback("econ.lb.prev", instance=self)(self.previous_button_callback)
        Button_Interaction_Handler.link_button_callback("econ.lb.next", instance=self)(self.next_button_callback)
        return await super().cog_load()

    async def cog_unload(self):
        Button_Interaction_Handler.unlink_button_callback("econ.lb.prev")
        Button_Interaction_Handler.unlink_button_callback("econ.lb.next")
        return await super().cog_unload()

async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard_Command(bot))