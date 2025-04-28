import discord
from discord.ext import commands
from datetime import datetime
from utils.adv_configparser import Advanced_ConfigParser
from utils.datetime_tools import get_elapsed_time_milliseconds, get_elapsed_time_smal
from utils.portal import Portal
import logging
from pathlib import Path
import traceback
from utils.database.psql_adapter import PostgreSQL_Adapter
from utils.database.main_controller import Main_DB_Controller
from utils.interaction_handler.button import Button_Interaction_Handler
from utils.interaction_handler.role_select import RoleSelect_Interaction_Handler
from utils.interaction_handler.custom_select import Select_Interaction_Handler

class Apollo_Bot(commands.Bot):
    def __init__(self, base_path:Path, startup_time:float):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=None, help_command=None, intents=intents)

        self.__portal:Portal
        self.__first_on_ready = False
        self.__base_path = base_path
        self.__startup_time = startup_time

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
        for cog_name in ["reload", "economy.currency", "economy.leaderboard", "economy.dailymoney", "economy.give", "gamble.group", "economy.pick", "economy.plant", 
                         "leveling.rank", "leveling.ranks", "setup.group", "leveling.turntoxp", "event.message.group", "leveling.group"]:
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
            startup_logger = logging.getLogger("app.startup")
            routine_start = datetime.now().timestamp()
            startup_logger.info("Starting execution of pre startup routine ...")
            await self.change_presence(status = discord.Status.dnd, activity = discord.CustomActivity("Executing pre startup routine (0/2)"))

            # Open the config for the database credentials
            database_config = Advanced_ConfigParser(Path.joinpath(self.__base_path, "config", "database.ini"))
            self.__portal.database_config = database_config
            await self.change_presence(status = discord.Status.dnd, activity = discord.CustomActivity("Executing pre startup routine (1/2)"))

            try:
                # Create the database connection
                psql_adapter = await PostgreSQL_Adapter.create_adapter(
                    database_config["POSTGRESQL"]["USERNAME"],
                    database_config["POSTGRESQL"]["PASSWORD"],
                    database_config["POSTGRESQL"]["DATABASE"],
                    database_config["POSTGRESQL"]["ADRESS"],
                    Path.joinpath(self.__base_path, "src"),
                    int(database_config["POSTGRESQL"]["PORT"])
                )
                controller = Main_DB_Controller(psql_adapter)
                self.__portal.database = controller
                await self.change_presence(status = discord.Status.online, activity = None)
            except Exception as error:
                traceback.print_exception(type(error), error, error.__traceback__)

            self.__first_on_ready = True
            startup_logger.info(f"Executed pre startup routine successfully after {get_elapsed_time_milliseconds(datetime.now().timestamp() - routine_start)}")
        else:
            startup_logger.info("Startup routine allready executed, omitting this execution")

    async def on_ready(self):
        logging.getLogger("app").info(f"Successfully logged in (after {get_elapsed_time_smal(datetime.now().timestamp() - self.__startup_time)}) as {self.user}")

    async def on_message(self, message):
        pass
