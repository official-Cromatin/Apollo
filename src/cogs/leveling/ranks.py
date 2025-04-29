import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.database.main_controller import Main_DB_Controller
import math
from tabulate import tabulate
from utils.calc_lvl_xp import calculate_current_level_experience
from utils.interaction_handler.button import Button_Interaction_Handler

class Ranks_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        super().__init__(logging.getLogger("cmds.ranks"))

    async def get_number_of_rank_pages(self, guild_id:int, page_size:int = 20) -> int:
        """Returns the number of pages that can be displayed for the ranking"""
        database:Main_DB_Controller = self.__bot.database
        return math.ceil(await database.get_number_of_level_users(guild_id) / page_size)
    
    async def get_next_page_number(self, message_id:int, increase:bool = True) -> int:
        """Returns the page number of the next page (starting with 0)
        
        When `increase` is `False`, it will be counted downwards, but never below zero"""
        database:Main_DB_Controller = self.__bot.database
        current_page = await database.get_ranks_page(message_id)
        if increase:
            current_page += 1
        else:
            current_page -= 1
            if current_page < 0:
                current_page = 0
        return current_page
    
    async def get_table(self, guild:discord.Guild, page:int = 0) -> str:
        """Creates the table containing a maximum of 20 entrys to display"""
        database:Main_DB_Controller = self.__bot.database
        users_info = await database.get_ranks_page_users(guild.id, page)
        table_data = []
        user_position = page * 1 + 1

        # Prepare the data for each table row
        for user_info in users_info:
            user_name = await self.__bot.hybrid_get_user(user_info[0])
            level_experience = calculate_current_level_experience(user_info[1])
            table_data.append((
                user_position, 
                user_name, 
                user_info[1],
                f"{user_info[2]} / {level_experience}",
                user_info[3]
            ))
            user_position += 1

        # Create the table
        headers = ["Rank", "Username", "Level", "XP", "Total XP"]
        return tabulate(table_data, headers = headers, tablefmt = "rounded_outline")
    
    async def get_message_content(self, ctx:discord.Interaction, current_page:int, number_of_pages:int) -> str:
        """Returns the message content for the ranks message (extracted functionality)"""
        table_content = await self.get_table(ctx.guild, current_page)
        return (
            f"## Ranks ({current_page + 1} / {number_of_pages})\n"
            f"```{table_content}```"
        )
    
    def get_view(self, current_page:int, number_of_pages:int) -> discord.ui.View:
        """Creates a new view with two buttons to change the current page"""
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Previous", custom_id = "ranks.prev", disabled = True if current_page == 0 else False))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Next", custom_id = "ranks.next", disabled = True if current_page == number_of_pages else False))
        return view

    @app_commands.command(name = "ranks", description = "Displays the global decending ranking link for this guild")
    @app_commands.describe(page = "Number of the page you want to display")
    async def ranks(self, ctx:discord.Interaction, page:int = 0):
        database:Main_DB_Controller = ctx.client.database
        if page < 0:
            await ctx.response.send_message("The page number must be greater than `0`", ephemeral = True)
            return
        elif page > 0:
            page -= 1
        
        # Check if the page number is valid
        number_of_pages = await self.get_number_of_rank_pages(ctx.guild_id)
        if number_of_pages - 1 < page:
            await ctx.response.send_message(f"Page {page + 1} does not exist, the last page is {number_of_pages}", ephemeral = True)
            return
        
        # Create and send the message for the current page
        message_content = await self.get_message_content(ctx, page, number_of_pages)
        view = self.get_view(page, number_of_pages - 1)
        await ctx.response.send_message(message_content, view = view)

        # Modify database
        message = await ctx.original_response()
        await database.create_ranks_view(message.id, page)

    async def callback_previous(self, ctx:discord.Interaction):
        """Called when a user interacts with the "Previous" button of the "ranks" view"""
        database:Main_DB_Controller = ctx.client.database
        next_page = await self.get_next_page_number(ctx.message.id, False)
        number_of_pages = await self.get_number_of_rank_pages(ctx.guild_id)

        # Create and send the message for the current page
        message_content = await self.get_message_content(ctx, next_page, number_of_pages)
        view = self.get_view(next_page, number_of_pages - 1)
        await ctx.response.edit_message(content = message_content, view = view)

        # Update database
        await database.set_ranks_page(ctx.message.id, next_page)

    async def callback_next(self, ctx:discord.Interaction):
        """Called when a user interacts with the "Next" button of the "ranks" view"""
        database:Main_DB_Controller = ctx.client.database
        next_page = await self.get_next_page_number(ctx.message.id, True)
        number_of_pages = await self.get_number_of_rank_pages(ctx.guild_id)

        # Create and send the message for the current page
        message_content = await self.get_message_content(ctx, next_page, number_of_pages)
        view = self.get_view(next_page, number_of_pages - 1)
        await ctx.response.edit_message(content = message_content, view = view)

        # Update database
        await database.set_ranks_page(ctx.message.id, next_page)

    async def cog_load(self):
        Button_Interaction_Handler.link_button_callback("ranks.prev", self)(self.callback_previous)
        Button_Interaction_Handler.link_button_callback("ranks.next", self)(self.callback_next)
        return await super().cog_load()
    
    async def cog_unload(self):
        Button_Interaction_Handler.unlink_button_callback("ranks.prev")
        Button_Interaction_Handler.unlink_button_callback("ranks.next")
        return await super().cog_unload()
            

async def setup(bot: commands.Bot):
    await bot.add_cog(Ranks_Command(bot))