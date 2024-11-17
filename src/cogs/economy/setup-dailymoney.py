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

class Dailymoney_Setup_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.maintenance"))
    
    def get_custom_select(self, placeholder:str, min_values:int, max_values:int, custom_id:str, min_priority:int, max_priority:int, priority_increment:int) -> discord.ui.Select:
        """"""
        menu = discord.ui.Select(placeholder = placeholder, min_values = min_values, max_values = max_values, custom_id = custom_id)
        for priority in range(min_priority, max_priority, priority_increment):
            menu.add_option(label = str(priority), value = str(priority))
        return menu
    
    def get_add_role_embed(self, role_id:int = None, priority:int = None, daily_salary:int = None) -> discord.Embed:
        """Generates the embed for the "add role" view"""
        for value in [role_id, priority, daily_salary]:
            if value is not None:
                note = ""
                break
        else:
            note = "\nUse the selection menus attatched to this message, to configure the properties"
        
        if role_id:
            role_id = f"<@&{role_id}>"
        else:
            role_id = "`None`"

        if priority:
            priority = f"`{priority}`"
        else:
            priority = "`None`"

        if daily_salary:
            daily_salary = f"`{daily_salary}` :dollar:"
        else:
            daily_salary = "`None`"

        embed = discord.Embed(
            title = "Add a additional role",
            description = f"""- Selected role: {role_id}
- Selected priority: {priority}
- Daily salary: {daily_salary}{note}""")
        embed.set_footer(text = "Tip: To add a new role, use the 'Add role' button of the main view")
        return embed
    
    def get_add_role_view(self, role_id:int = None, priority:int = None, daily_salary:int = None) -> discord.ui.View:
        """Creates the view for the "add role" view depending on the state of the other values"""
        save_disabled = False
        for value in [role_id, priority, daily_salary]:
            if value is None:
                save_disabled = True

        if role_id:
            selected_role = [discord.SelectDefaultValue(id = role_id, type = discord.SelectDefaultValueType.role)]
        else:
            selected_role = []

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.green, label = "Save", custom_id = "setup.dm.add.save", disabled = save_disabled))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.red, label = "Discard", custom_id = "setup.dm.add.disc"))
        
        view.add_item(discord.ui.RoleSelect(placeholder = "Select additional role", min_values = 1, max_values = 1, custom_id = "setup.dm.add.role", default_values = selected_role))
        view.add_item(self.get_custom_select("Select priority for role", 1, 1, "setup.dm.add.prio", 1, 26, 1))
        view.add_item(self.get_custom_select("Define daily income", 1, 1, "setup.dm.add.sala", 10, 130, 5))
        return view
    
    async def get_main_view_description(self, guild:discord.Guild) -> str:
        """Get the description for the main view embed"""
        roles:list = await self.__portal.database.get_dailymoney_roles(guild.id)
        print("ROLES", roles)
        if roles:
            table_data = []
            for role_data in roles:
                table_data.append([
                    role_data[0],
                    guild.get_role(role_data[1]),
                    role_data[2]
                ])

            headers = ["Priority", "Name of role", "Salary"]
            table_content = tabulate(table_data, headers = headers, tablefmt = "rounded_outline")
        else:
            table_content = "No roles have been defined yet."

        return_str = f"""*Note: To see the manual for this featureset, click the help button below*
Current roles and their priorities:
```
{table_content}
```"""

        return return_str
    
    setup_group = app_commands.Group(name = "setup", description = "Contains commands neccessary to setup different modules")
    @setup_group.command(name = "dailymoney", description = "Opens the main setup view for the dailymoney configuration")
    async def setup_dailymoney(self, ctx: discord.Interaction):
        embed = discord.Embed(title = "Influencing roles for the daily salary on this server", description = await self.get_main_view_description(ctx.guild))
        embed.set_footer(text = "Tip: To edit priorities and the amount of income, use the buttons below")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Add role", custom_id = "setup.dm.add"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Change role priority", custom_id = "setup.dm.edit"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.red, label = "Delete role", custom_id = "setup.dm.del"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.red, label = "Help", custom_id = "setup.dm.help"))

        await ctx.response.send_message(embed = embed, view = view)

    async def callback_button_add_role(self, ctx: discord.Interaction):
        """Called when a user interacts with the "add role" button of the main view"""
        embed = self.get_add_role_embed()
        view = self.get_add_role_view()

        await ctx.response.send_message(embed = embed, view = view)
        message: discord.InteractionMessage = await ctx.original_response()
        await self.__portal.database.create_add_role_message(ctx.message.id, message.id)

    async def callback_select_role(self, ctx: discord.Interaction):
        """Called when a user interacts with the role selector of the "add role" view"""
        selected_role_id = int(ctx.data["values"][0])
        if await self.__portal.database.check_dailymoney_role_presence(ctx.guild_id, selected_role_id):
            await ctx.response.send_message("This role is already selected!", ephemeral = True)
            return

        await self.__portal.database.set_role_for_role_message(ctx.message.id, selected_role_id)

        message_data = await self.__portal.database.get_role_message_data(ctx.message.id)
        await ctx.response.edit_message(
            embed = self.get_add_role_embed(message_data[0], message_data[1], message_data[2]),
            view = self.get_add_role_view(message_data[0], message_data[1], message_data[2]))

    async def callback_select_priority(self, ctx: discord.Interaction):
        """Called when a user interacts with the priority selector of the "add_role" view"""
        selected_priority = int(ctx.data["values"][0])
        await self.__portal.database.set_priority_for_role_message(ctx.message.id, selected_priority)

        message_data = await self.__portal.database.get_role_message_data(ctx.message.id)
        await ctx.response.edit_message(
            embed = self.get_add_role_embed(message_data[0], message_data[1], message_data[2]),
            view = self.get_add_role_view(message_data[0], message_data[1], message_data[2]))
    
    async def callback_select_daily_salary(self, ctx: discord.Interaction):
        """Called when a user interacts with the daily income selector of the "add role" view"""
        daily_income = int(ctx.data["values"][0])
        await self.__portal.database.set_salary_for_role_message(ctx.message.id, daily_income)

        message_data = await self.__portal.database.get_role_message_data(ctx.message.id)
        await ctx.response.edit_message(
            embed = self.get_add_role_embed(message_data[0], message_data[1], message_data[2]),
            view = self.get_add_role_view(message_data[0], message_data[1], message_data[2]))
        
    async def callback_add_save(self, ctx: discord.Interaction):
        """Called when a user interacts with the "Save" button of the "add role" view"""
        message_data = await self.__portal.database.get_role_message_data(ctx.message.id)
        if await self.__portal.database.check_dailymoney_role_presence(ctx.guild_id, message_data[0]):
            ctx.response.send_message("The role was already added to the dailymoney roles set.\nSelect another role or discard this view", ephemeral = True)
            return
        
        await self.__portal.database.add_dailymoney_role(ctx.guild_id, message_data[1], message_data[0], message_data[2])
        await ctx.response.send_message("Successfully added the role.", ephemeral = True)
        await self.__portal.database.remove_dailymoney_add_role_message(ctx.message.id)
        await ctx.message.delete()
        await self.update_main_view(ctx.guild, ctx.channel)

    async def callback_add_discard(self, ctx: discord.Interaction):
        """Called when a user interacts with the "Discard" button of the "add role" view"""
        await self.__portal.database.remove_dailymoney_add_role_message(ctx.message.id)
        await ctx.message.delete()

    async def callback_button_help(self, ctx: discord.Interaction):
        """Called when a user interacts with the "help" button of the main view"""
        embed = discord.Embed(
            title = "Description of the scope of functions",
            description = """
### Main view
This view shows you (in order of priority) which priority they have and how much income they receive per day
It allows you to open other settings windows, but only one window can be opened at a time!

### Add new role
Before a new role can be added, you must select the role itself, its priority and the amount of daily salary

### Change priority
If you want to change aspects such as the priority or amount of daily salary, you must use this configuration view.
It also allows you to remove a role directly, for which you only need to select the role

### Remove role
A role can be removed here, remember that the action cannot be revoked!""")
        
        await ctx.response.send_message(embed = embed, ephemeral = True)

    async def cog_load(self):
        Button_Interaction_Handler.link_button_callback("setup.dm.add", self)(self.callback_button_add_role)
        Button_Interaction_Handler.link_button_callback("setup.dm.help", self)(self.callback_button_help)
        RoleSelect_Interaction_Handler.link_button_callback("setup.dm.add.role", self)(self.callback_select_role)
        Select_Interaction_Handler.link_button_callback("setup.dm.add.prio", self)(self.callback_select_priority)
        Select_Interaction_Handler.link_button_callback("setup.dm.add.sala", self)(self.callback_select_daily_salary)
        Button_Interaction_Handler.link_button_callback("setup.dm.add.save", self)(self.callback_add_save)
        Button_Interaction_Handler.link_button_callback("setup.dm.add.disc", self)(self.callback_add_discard)
        return await super().cog_load()

    async def cog_unload(self):
        for pre in ["setup.dm.add", "setup.dm.edit", "setup.dm.del", "setup.dm.help"]:
            Button_Interaction_Handler.unlink_button_callback(pre)
        RoleSelect_Interaction_Handler.unlink_button_callback("setup.dm.add.role")
        Select_Interaction_Handler.unlink_button_callback("setup.dm.add.prio")
        Select_Interaction_Handler.unlink_button_callback("setup.dm.add.sala")
        Select_Interaction_Handler.unlink_button_callback("setup.dm.add.save")
        Select_Interaction_Handler.unlink_button_callback("setup.dm.add.disc")
        return await super().cog_unload()

async def setup(bot: commands.Bot):
    await bot.add_cog(Dailymoney_Setup_Command(bot))