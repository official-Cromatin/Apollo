from utils.singleton import Singleton
from utils.adv_configparser import Advanced_ConfigParser

@Singleton
class Portal:
    PROGRAM_VERSION = "0.3"
    bot_config:Advanced_ConfigParser = None
    STARTUP_TIMESTAMP:float = None
    no_executed_commands:int = 0
    no_succeeded_commands:int = 0
    no_failed_commands:int = 0