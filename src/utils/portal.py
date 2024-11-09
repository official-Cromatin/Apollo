from utils.singleton import Singleton
from utils.adv_configparser import Advanced_ConfigParser
from utils.database.main_controller import Main_DB_Controller

@Singleton
class Portal:
    PROGRAM_VERSION = "0.3"
    bot_config:Advanced_ConfigParser = None
    database_config:Advanced_ConfigParser = None
    database:Main_DB_Controller
    STARTUP_TIMESTAMP:float = None
    no_executed_commands:int = 0
    no_succeeded_commands:int = 0
    no_failed_commands:int = 0