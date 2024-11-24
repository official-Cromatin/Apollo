import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal
from utils.interaction_handler.button import Button_Interaction_Handler
from utils.interaction_handler.role_select import RoleSelect_Interaction_Handler
from utils.interaction_handler.custom_select import Select_Interaction_Handler
from tabulate import tabulate
from typing import Literal

class Dailymoney_Setup_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot:discord.Client = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.setup.dailymoney"))

    # Create command group and group command
    setup_group = app_commands.Group(name = "setup", description = "Contains commands neccessary to setup different modules")
    @setup_group.command(name = "dailymoney", description = "Opens the main setup view for the dailymoney configuration")
    async def setup_dailymoney(self, ctx: discord.Interaction):
        embed = discord.Embed(title = "Influencing roles for the daily salary on this server", description = await self.get_main_view_description(ctx.guild))
        embed.set_footer(text = "Tip: To edit priorities and the amount of income, use the buttons below")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Add role", custom_id = "setup.dm.add"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Edit role settings", custom_id = "setup.dm.edit"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.red, label = "Delete role", custom_id = "setup.dm.del"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.red, label = "Help", custom_id = "setup.dm.help"))

        await ctx.response.send_message(embed = embed, view = view)

    # Utility methods containing extracted functionality
    def get_custom_select(self, placeholder:str, min_values:int, max_values:int, custom_id:str, min_priority:int, max_priority:int, priority_increment:int) -> discord.ui.Select:
        """Creates a discord.ui.Select object altered by the provided arguments"""
        menu = discord.ui.Select(placeholder = placeholder, min_values = min_values, max_values = max_values, custom_id = custom_id)
        for priority in range(min_priority, max_priority, priority_increment):
            menu.add_option(label = str(priority), value = str(priority))
        return menu
    
    def get_role_embed(self, embed_title:str, role_id:int = None, priority:int = None, daily_salary:int = None) -> discord.Embed:
        """Generates the embed for the "add role" and "edit role" view"""
        note = "\nUse the selection menus attached to this message, to configure the properties" \
        if any(value is None for value in [role_id, priority, daily_salary]) else ""
        
        role_id = f"<@&{role_id}>" if role_id else "`None`"
        priority = f"`{priority}`" if priority else "`None`"
        daily_salary = f"`{daily_salary}` :dollar:" if daily_salary else "`None`"

        description = (
        f"- **Selected role**: {role_id}\n"
        f"- **Selected priority**: {priority}\n"
        f"- **Daily salary**: {daily_salary}"
        f"{note}"
        )

        embed = discord.Embed(
            title = embed_title,
            description = description
        )
        embed.set_footer(text = "Tip: To add a new role, use the 'Add role' button of the main view")
        return embed

    def get_role_view(self, view_type:Literal["add", "edit"], role_id:int = None, priority:int = None, daily_salary:int = None) -> discord.ui.View:
        """Creates the view for the role setup (add/edit), depending on the given state"""
        # Define constants for custom select menus
        SALARY_MIN = 10         # Default: 10
        SALARY_MAX = 130        # Default: 130
        SALARY_INCREMENT = 5    # Default: 5

        PRIORITY_MIN = 1        # Default: 1
        PRIOTITY_MAX = 25       # Default: 25
        
        # Determine state of the save button, if state is "add"
        save_disabled = view_type == "add" and any(value is None for value in [role_id, priority, daily_salary])

        # If role_id is given, select it in the role view
        selected_role = [discord.SelectDefaultValue(id=role_id, type=discord.SelectDefaultValueType.role)] if role_id else []

        # Create the view itself
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.green,
            label="Save",
            custom_id=f"setup.dm.edit.save",
            disabled=save_disabled
        ))
        view.add_item(discord.ui.Button(
            style=discord.ButtonStyle.red,
            label="Discard",
            custom_id=f"setup.dm.edit.disc"
        ))

        # Add select menu for the roles
        role_placeholder = "Select additional role" if view_type == "add" else "Select existing role"
        view.add_item(discord.ui.RoleSelect(
            placeholder=role_placeholder,
            min_values=1,
            max_values=1,
            custom_id=f"setup.dm.edit.role",
            default_values=selected_role
        ))

        # Add custom selects for priority and salary
        view.add_item(self.get_custom_select(
            "Select priority for role", 1, 1, f"setup.dm.edit.prio", PRIORITY_MIN, PRIOTITY_MAX+1, 1
        ))
        view.add_item(self.get_custom_select(
            "Define daily income", 1, 1, f"setup.dm.edit.sala", SALARY_MIN, SALARY_MAX, SALARY_INCREMENT
        ))

        return view

    async def get_main_view_description(self, guild:discord.Guild) -> str:
        """Get the description for the main view embed"""
        roles:list = await self.__portal.database.get_dailymoney_roles(guild.id)
        if roles:
            # Prepare and sort table data
            table_data = []
            for role_data in roles:
                table_data.append([
                    role_data[0],
                    guild.get_role(role_data[1]) or "[ROLE DELETED]",
                    role_data[2]
                ])
            table_data.sort(key=lambda x: x[0], reverse=True)

            # Format table with tabulate
            headers = ["Priority", "Name of Role", "Salary"]
            table_content = tabulate(table_data, headers=headers, tablefmt="rounded_outline")
        else:
            table_content = "No roles have been defined yet."

        return (
            "*Note: To see the manual for this featureset, click the help button below*\n"
            "Current roles and their priorities:\n"
            f"```{table_content}```"
        )
    
    async def update_main_view(self, ctx:discord.Interaction, message_id:int):
        """Updates the main view message"""
        # Get channel
        channel:discord.guild.GuildChannel = self.__bot.get_channel(ctx.channel_id)
        if channel:
            try:
                # Fetch message
                message:discord.Message = await channel.fetch_message(message_id)
                # Update the message if the bot was the author of the message
                if message.author == self.__bot.user:
                    embed = discord.Embed(title = "Influencing roles for the daily salary on this server", description = await self.get_main_view_description(ctx.guild))
                    embed.set_footer(text = "Tip: To edit priorities and the amount of income, use the buttons below")
                    await message.edit(embed = embed)
                    self._logger.debug(f"Successfully updated main view message {message_id}")
                else:
                    self._logger.error(f"Message {message_id} in {ctx.channel_id} was not created by the bot")
            except discord.NotFound:
                self._logger.error(f"Message {message_id} in {ctx.channel_id} was not found. Maybe deleted?")
            except discord.Forbidden:
                self._logger.error(f"Insufficient permissions to load message {message_id} in {ctx.channel_id}")

    async def update_edit_view(self, ctx:discord.Interaction):
        """Updates the edit role view message. Involves creating the embed aswell as the view"""
        message_data = await self.__portal.database.get_role_message_data(ctx.message.id)
        view_type = "add" if message_data[4] == 0 else "edit"

        await ctx.response.edit_message(
            embed = self.get_role_embed("Add additional role", message_data[0], message_data[1], message_data[2]),
            view = self.get_role_view(view_type, message_data[0], message_data[1], message_data[2]))
        self._logger.debug(f"Updated '{view_type} role' view message {ctx.message.id}")

    # Callback handlers used to create additional views
    async def callback_button_add_role(self, ctx: discord.Interaction):
        """Called when a user interacts with the "add role" button of the main view"""
        embed = self.get_role_embed("Add additional role")
        view = self.get_role_view("add")

        await ctx.response.send_message(embed = embed, view = view)
        message: discord.InteractionMessage = await ctx.original_response()
        await self.__portal.database.create_role_message(ctx.message.id, message.id, 0)

    async def callback_button_edit(self, ctx: discord.Interaction):
        """Called when a user interacts with the "edit role settings" button of the main view"""
        embed = self.get_role_embed("Edit existing role")
        view = self.get_role_view("edit")

        await ctx.response.send_message(embed = embed, view = view)
        message: discord.InteractionMessage = await ctx.original_response()
        await self.__portal.database.create_role_message(ctx.message.id, message.id, 1)

    async def callback_button_help(self, ctx: discord.Interaction):
        """Called when a user interacts with the "help" button of the main view"""
        embed = discord.Embed(
            title = "Description of the scope of functions",
            description = (
                "### Main view\n"
                "This view shows you (in order of priority) which priority they have and how much income they receive per day\n"
                "It allows you to open other settings windows, but only one window can be opened at a time!\n"

                "### Add new role\n"
                "Before a new role can be added, you must select the role itself, its priority and the amount of daily salary\n"

                "### Change priority\n"
                "If you want to change aspects such as the priority or amount of daily salary, you must use this configuration view.\n"
                "It also allows you to remove a role directly, for which you only need to select the role\n"

                "### Remove role\n"
                "A role can be removed here, remember that the action cannot be revoked!\n"
            )
        )
        await ctx.response.send_message(embed = embed, ephemeral = True)

    # Callback handlers for select menus
    async def callback_select_role(self, ctx: discord.Interaction):
        """Called when a user interacts with the role selector of the "add role" view"""
        selected_role_id = int(ctx.data["values"][0])
        guild_role_ids:list[int] = await self.__portal.database.get_role_ids_for_guild(ctx.guild_id)
        match await self.__portal.database.get_dailymoney_edit_mode(ctx.message.id):
            case 0: # Add additional role
                # Check if selected role is part of dailymoney roles on that guild
                if selected_role_id in guild_role_ids:
                    await ctx.response.send_message("This role is already selected!\nSelect an role that hasnt been added yet", ephemeral = True)
                    return
                
                # Update main message
                await self.__portal.database.set_role_for_role_message(ctx.message.id, selected_role_id)
                await self.update_edit_view(ctx)
                
            case 1: # Modify settings of existing role
                # Check that role is part is dailymoney roles
                if selected_role_id not in guild_role_ids:
                    await ctx.response.send_message("This role isnt part of the dailymoney roles!\nSelect an role that has been added yet", ephemeral = True)
                    return
                
                # Fill in data specified in the dailymoney_role table
                await self.__portal.database.update_settings_from_role(selected_role_id, ctx.message.id)

                # Update main message
                await self.__portal.database.set_role_for_role_message(ctx.message.id, selected_role_id)
                await self.update_edit_view(ctx)

    async def callback_select_priority(self, ctx: discord.Interaction):
        """Called when a user interacts with the priority selector of the "add_role" view"""
        selected_priority = int(ctx.data["values"][0])
        await self.__portal.database.set_priority_for_role_message(ctx.message.id, selected_priority)

        # Update the message
        await self.update_edit_view(ctx)
    
    async def callback_select_daily_salary(self, ctx: discord.Interaction):
        """Called when a user interacts with the daily income selector of the "add role" view"""
        daily_income = int(ctx.data["values"][0])
        await self.__portal.database.set_salary_for_role_message(ctx.message.id, daily_income)

        # Update the message
        await self.update_edit_view(ctx)
    
    # Callback handlers for buttons of the "add role" and "edit role" views
    async def callback_add_save(self, ctx: discord.Interaction):
        """Called when a user interacts with the "Save" button of the "add role" view"""
        message_data = await self.__portal.database.get_role_message_data(ctx.message.id)
        guild_role_ids:list[int] = await self.__portal.database.get_role_ids_for_guild(ctx.guild_id)

        match message_data[4]:
            case 0:
                if message_data[0] in guild_role_ids:
                    await ctx.response.send_message("The role was already added to the dailymoney roles set.\nSelect another role or discard this view", ephemeral = True)
                    return
                await self.__portal.database.add_dailymoney_role(ctx.guild_id, message_data[1], message_data[0], message_data[2])


            case 1:
                if message_data[0] not in guild_role_ids:
                    await ctx.response.send_message("The role was already added to the dailymoney roles set.\nSelect another role or discard this view", ephemeral = True)
                    return
                await self.__portal.database.update_dailymoney_role(message_data[0], message_data[1], message_data[2])

        await self.__portal.database.remove_dailymoney_add_role_message(ctx.message.id)
        await ctx.message.delete()
        await self.update_main_view(ctx, message_data[3])
        await ctx.response.send_message("Successfully altered the settings", ephemeral = True)

    async def callback_add_discard(self, ctx: discord.Interaction):
        """Called when a user interacts with the "Discard" button of the "add role" view"""
        await self.__portal.database.remove_dailymoney_add_role_message(ctx.message.id)
        await ctx.message.delete()

    # Override methods to add additional functionality in order to create links, neccessary to handle interactions
    async def cog_load(self):
        # Establish links for the "main view"
        Button_Interaction_Handler.link_button_callback("setup.dm.add", self)(self.callback_button_add_role)
        Button_Interaction_Handler.link_button_callback("setup.dm.edit", self)(self.callback_button_edit)
        # TO-DO: Link for "delete role" view
        Button_Interaction_Handler.link_button_callback("setup.dm.help", self)(self.callback_button_help)

        # Establish links for the "add role" and "edit role" view
        Button_Interaction_Handler.link_button_callback("setup.dm.edit.save", self)(self.callback_add_save)
        Button_Interaction_Handler.link_button_callback("setup.dm.edit.disc", self)(self.callback_add_discard)
        RoleSelect_Interaction_Handler.link_button_callback("setup.dm.edit.role", self)(self.callback_select_role)
        Select_Interaction_Handler.link_button_callback("setup.dm.edit.prio", self)(self.callback_select_priority)
        Select_Interaction_Handler.link_button_callback("setup.dm.edit.sala", self)(self.callback_select_daily_salary)
        
        return await super().cog_load()

    async def cog_unload(self):
        # Unlink links for the "main view"
        for pre in ["setup.dm.add", "setup.dm.edit", "setup.dm.del", "setup.dm.help"]:
            Button_Interaction_Handler.unlink_button_callback(pre)

        # Unlink links for the "add role" and "edit role" view
        Select_Interaction_Handler.unlink_button_callback("setup.dm.edit.save")
        Select_Interaction_Handler.unlink_button_callback("setup.dm.edit.disc")
        RoleSelect_Interaction_Handler.unlink_button_callback("setup.dm.edit.role")
        Select_Interaction_Handler.unlink_button_callback("setup.dm.edit.prio")
        Select_Interaction_Handler.unlink_button_callback("setup.dm.edit.sala")

        return await super().cog_unload()

async def setup(bot: commands.Bot):
    await bot.add_cog(Dailymoney_Setup_Command(bot))