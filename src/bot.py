import discord
from discord.ext import commands
from datetime import datetime
from utils.adv_configparser import Advanced_ConfigParser
from utils.datetime_tools import get_elapsed_time_milliseconds, get_elapsed_time_smal
import logging
from pathlib import Path
import traceback
from utils.database.psql_adapter import PostgreSQL_Adapter
from utils.database.main_controller import Main_DB_Controller
from utils.interaction_handler.button import Button_Interaction_Handler
from utils.interaction_handler.role_select import RoleSelect_Interaction_Handler
from utils.interaction_handler.custom_select import Select_Interaction_Handler
from utils.database.sql_loader import SQL_Loader, Database_Types
import asyncpg

class Apollo_Bot(commands.Bot):
    def __init__(self, base_path:Path, startup_time:float, program_version:str):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=None, help_command=None, intents=intents)

        self.PROGRAM_VERSION = program_version
        self.__first_on_ready = False
        self.__base_path = base_path
        self.__startup_time = startup_time
        self.__database:PostgreSQL_Adapter
        self.__new_database_conn:asyncpg.Connection
        self.__active_views:dict[int] = {}
        self.__sql_loader:SQL_Loader = None

    async def hybrid_get_user(self, user_id:int) -> discord.User | None:
        """Returns a user with the given ID
        
        First tries [`get_user`](https://discordpy.readthedocs.io/en/stable/api.html?highlight=get_user#discord.Client.get_user) and if it fails, [`fetch_user`](https://discordpy.readthedocs.io/en/stable/api.html?highlight=fetch_user#discord.Client.fetch_user) as an fallback"""
        user = self.get_user(user_id)
        if user:
            return user
        return await self.fetch_user(user_id)

    async def setup_hook(self):
        # Load the database extensions
        self.__sql_loader = SQL_Loader(Database_Types.POSTGRESQL, self.__base_path / "src" / "database")
        for database_model_name in ["saved_state.model"]:
            await self.load_extension(f"database.models.{database_model_name}")

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

                    from database.models.saved_state.model import Saved_State
                    from database.models.saved_state.enum import View_Names
                    from database.models.base_model.exceptions import NotFound

                    if interaction.message.id in self.__active_views:
                        logging.getLogger("view").debug("Skipped view recovery as its still active", extra={"iname": self.__active_views[interaction.message.id].view_name.name, "id": interaction.message.id})
                    else:
                        try:
                            state = await Saved_State.load(self.__new_database_conn, interaction.guild.id, interaction.channel.id, interaction.message.id)
                        except NotFound:
                            logging.getLogger("view").error(f"Unable to restore view for message {interaction.message.id}, no saved state found")
                        else:
                            match state.view_name:

                                case _:
                                    raise Exception("View not found")
                            
                            await interaction.message.edit(view = view)
                            view.activate()
                            await view.save_state()
                            callback = view.identify_callback(interaction.data["custom_id"])
                            await callback(interaction)

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
                self.__database = controller
                self.__new_database_conn = await asyncpg.connection.connect(
                    user = database_config["POSTGRESQL"]["USERNAME"],
                    password = database_config["POSTGRESQL"]["PASSWORD"],
                    database = database_config["POSTGRESQL"]["DATABASE"],
                    host = database_config["POSTGRESQL"]["ADRESS"],
                    port = int(database_config["POSTGRESQL"]["PORT"])
                )
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

    @property
    def database(self) -> PostgreSQL_Adapter:
        """Main_DB_Controller wich handles every request to the database for this bot"""
        return self.__database
    
    @property
    def new_database(self) -> asyncpg.Connection:
        """Database connection for this bot instance"""
        return self.__new_database_conn
    
    @property
    def sql_loader(self) -> SQL_Loader:
        """SQL_Loader wich handles the loading of the .sql files"""
        return self.__sql_loader

    @property
    def active_views(self) -> dict[int, discord.ui.View]:
        """Dictionary containin all active views for this bot instance"""
        return self.__active_views
