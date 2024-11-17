import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal
from utils.interaction_handler.button import Button_Interaction_Handler
from tabulate import tabulate

class Dailymoney_Setup_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.maintenance"))
    
    setup_group = app_commands.Group(name = "setup", description = "Contains commands neccessary to setup different modules")
    @setup_group.command(name = "dailymoney", description = "Opens the main setup view for the dailymoney configuration")
    async def setup_dailymoney(self, ctx: discord.Interaction):
        roles:list = await self.__portal.database.get_dailymoney_roles(ctx.guild_id)
        print("ROLES", roles)
        if roles:
            table_data = []
            for role_data in roles:
                table_data.append([
                    role_data[0],
                    ctx.guild.get_role(role_data[1]),
                    role_data[2]
                ])

            headers = ["Priority", "Name of role", "Salary"]
            table_content = tabulate(table_data, headers = headers, tablefmt = "rounded_outline")
        else:
            table_content = "No roles have been defined yet."


        embed = discord.Embed(title = "Influencing roles for the daily salary on this server", description = f"""
*Note: To see the manual for this featureset, click the help button below*

Current roles and their priorities:
```
{table_content}
```""")
        embed.set_footer(text = "Tip: To edit priorities and the amount of income, use the buttons below")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Add role", custom_id = "setup.dm.add"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.blurple, label = "Change role priority", custom_id = "setup.dm.edit"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.red, label = "Delete role", custom_id = "setup.dm.del"))
        view.add_item(discord.ui.Button(style = discord.ButtonStyle.red, label = "Help", custom_id = "setup.dm.help"))

        await ctx.response.send_message(embed = embed, view = view)

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
        return await super().cog_load()

    async def cog_unload(self):
        for pre in ["setup.dm.add", "setup.dm.edit", "setup.dm.del", "setup.dm.help"]:
            Button_Interaction_Handler.unlink_button_callback(pre)
        return await super().cog_unload()

async def setup(bot: commands.Bot):
    await bot.add_cog(Dailymoney_Setup_Command(bot))