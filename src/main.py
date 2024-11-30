print("      ___    ____  ____  __    __    ____  ")
print("     /   |  / __ \/ __ \/ /   / /   / __ \ ")
print("    / /| | / /_/ / / / / /   / /   / / / / ")
print("   / ___ |/ ____/ /_/ / /___/ /___/ /_/ /  ")
print("  /_/  |_/_/    \____/_____/_____/\____/   ")
print("  Copyright (c) 2024 Cromatin              ")
print()
print("  Source: https://github.com/official-Cromatin/Apollo")
print("  Report an Issue: https://github.com/official-Cromatin/Apollo/issues/new?assignees=&labels=bug&projects=&template=issue_report.yml")
print("\n")

from datetime import datetime
startup_time = datetime.now().timestamp()

# Initialize the logger
from utils.logger.custom_logging import Custom_Logger
Custom_Logger.initialize()

import logging
app_logger = logging.getLogger("app")
app_logger.info("Starting Apollo ...")
startup_logger = logging.getLogger("app.startup")

# Import all the remaining dependencies
import discord
from discord.ext import commands
from pathlib import Path
from utils.portal import Portal
from utils.datetime_tools import get_elapsed_time_smal, get_elapsed_time_big, get_elapsed_time_milliseconds
from utils.adv_configparser import Advanced_ConfigParser
import re
import traceback
import asyncio
from utils.database.psql_adapter import PostgreSQL_Adapter
from utils.database.main_controller import Main_DB_Controller
import sys
from utils.interaction_handler.button import Button_Interaction_Handler
from utils.interaction_handler.role_select import RoleSelect_Interaction_Handler
from utils.interaction_handler.custom_select import Select_Interaction_Handler

source_path = Path(__file__).resolve()
base_path = source_path.parents[1]
app_logger.info(f"Using the following path as entrypoint: '{base_path}'")

class Apollo_Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.members = True
        super().__init__(command_prefix=None, help_command=None, intents=intents)

        self.__portal:Portal
        self.__first_on_ready = False

    def set_portal(self, portal:Portal):
        self.__portal = portal

    async def hybrid_get_user(self, user_id:int) -> discord.User | None:
        """Returns a user with the given ID
        
        First tries [`get_user`](https://discordpy.readthedocs.io/en/stable/api.html?highlight=get_user#discord.Client.get_user) and if it fails, [`fetch_user`](https://discordpy.readthedocs.io/en/stable/api.html?highlight=fetch_user#discord.Client.fetch_user) as an fallback"""
        user = self.get_user(user_id)
        if user:
            return user
        return await self.fetch_user(user_id)

    async def setup_hook(self):
        # Register cogs to handle commands
        for cog_name in ["reload", "economy.currency", "economy.leaderboard", "economy.setup-dailymoney", "economy.dailymoney", "economy.give"]:
            await self.load_extension(f"cogs.{cog_name}")
        await self.tree.sync()

    async def on_interaction(self, interaction: discord.Interaction):
        """Called when an interaction happened"""
        try:
            match interaction.type.name:
                case discord.InteractionType.application_command.name:
                    print("Interaction with bot", interaction.command.name)
                    # self.__portal.no_executed_commands += 1
                case discord.InteractionType.ping.name:
                    print("App got pinged by discord")
                case discord.InteractionType.autocomplete.name:
                    print("Interaction with autocomplete")
                case discord.InteractionType.modal_submit.name:
                    print("Modal interaction submitted")
                case discord.InteractionType.component.name:
                    match discord.ComponentType(interaction.data["component_type"]):
                        case discord.ComponentType.button:
                            print("Component interaction with button")
                            await Button_Interaction_Handler.handle_interaction(interaction)
                        case discord.ComponentType.role_select:
                            print("Component interaction with role-select menu")
                            await RoleSelect_Interaction_Handler.handle_interaction(interaction)
                        case discord.ComponentType.select:
                            print("Component interaction with custom select menu")
                            await Select_Interaction_Handler.handle_interaction(interaction)
                        case _:
                            print(f"Component interaction with {interaction.data['component_type']}")
                            print(type(discord.ComponentType.button), type(interaction.data['component_type']))
        except Exception as error:
            traceback.print_exception(type(error), error, error.__traceback__)

    async def on_connect(self):
        """A coroutine to be called to setup the bot, after the bot is logged in but before it has connected to the Websocket"""
        if not self.__first_on_ready:
            routine_start = datetime.now().timestamp()
            startup_logger.info("Starting execution of pre startup routine ...")
            await self.change_presence(status = discord.Status.dnd, activity = discord.CustomActivity("Executing pre startup routine (0/2)"))

            # Open the config for the database credentials
            database_config = Advanced_ConfigParser(Path.joinpath(base_path, "config", "database.ini"))
            portal.database_config = database_config
            await self.change_presence(status = discord.Status.dnd, activity = discord.CustomActivity("Executing pre startup routine (1/2)"))

            try:
                # Create the database connection
                psql_adapter = await PostgreSQL_Adapter.create_adapter(
                    database_config["POSTGRESQL"]["USERNAME"],
                    database_config["POSTGRESQL"]["PASSWORD"],
                    database_config["POSTGRESQL"]["DATABASE"],
                    database_config["POSTGRESQL"]["ADRESS"],
                    Path.joinpath(base_path, "src"),
                    int(database_config["POSTGRESQL"]["PORT"])
                )
                controller = Main_DB_Controller(psql_adapter)
                portal.database = controller
                await self.change_presence(status = discord.Status.online, activity = None)
            except Exception as error:
                traceback.print_exception(type(error), error, error.__traceback__)

            self.__first_on_ready = True
            startup_logger.info(f"Executed pre startup routine successfully after {get_elapsed_time_milliseconds(datetime.now().timestamp() - routine_start)}")
        else:
            startup_logger.info("Startup routine allready executed, omitting this execution")

    async def on_ready(self):
        app_logger.info(f"Successfully logged in (after {get_elapsed_time_smal(datetime.now().timestamp() - startup_time)}) as {self.user}")

# Create
bot = Apollo_Bot()
bot_config = Advanced_ConfigParser(Path.joinpath(base_path, "config", "bot.ini"))
if re.match(r'[A-Za-z\d]{24}\.[\w-]{6}\.[\w-]{27}', bot_config["DISCORD"]["TOKEN"]):
    app_logger.critical("Bot (config/bot.ini) configuration invalid, please set a valid token")
    quit(1)
elif bot_config.compare_to_template() not in ("equal", "config_minus"):
    app_logger.critical("Bot (config/bot.ini) configuration is missing some parts. Make sure it at least has all the same keys as the template")
    quit(1)
else:
    app_logger.info("Bot configuration valid, continuing with startup")

# Execute some housekeeping actions
portal = Portal.instance()
portal.bot_config = bot_config
portal.STARTUP_TIMESTAMP = startup_time
bot.set_portal(portal)

# Setup handlers to handle states of command execution
@bot.tree.error
async def on_app_command_error(ctx:discord.Interaction, error):
    """Executed when exception during command execution occurs"""
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__)

    portal.no_failed_commands += 1

try:
    bot.run(bot_config["DISCORD"]["TOKEN"], log_handler = None)
except discord.errors.LoginFailure:
    app_logger.critical("Improper token has been passed. Aborting startup")
    quit(1)

app_logger.info("Quitting application ...")
asyncio.run(bot.close())
app_logger.info(f"Exiting. Application ran for {get_elapsed_time_big(datetime.now().timestamp() - startup_time)}")
