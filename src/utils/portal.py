from utils.singleton import Singleton
from utils.adv_configparser import Advanced_ConfigParser

@Singleton
class Portal:
    PROGRAM_VERSION = "0.3"
    bot_config:Advanced_ConfigParser = None
    STARTUP_TIMESTAMP:float = None
    source_path:str = None