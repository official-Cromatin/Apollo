import logging
from utils.logger.formatter import Colored_Formatter

class Custom_Logger:
    console_handler: logging.StreamHandler
    colored_formatter: Colored_Formatter
    
    @classmethod
    def initialize(cls):
        # Create the handler for logging to the console
        cls.console_handler = logging.StreamHandler()
        cls.console_handler.setLevel(logging.DEBUG)

        # Create the colorful formatter
        cls.colored_formatter = Colored_Formatter()
        cls.console_handler.setFormatter(cls.colored_formatter)

        # Create the loggers for the different sections of the app
        discordpy_logger = logging.getLogger("discord")
        discordpy_logger.addHandler(cls.console_handler)
        discordpy_logger.setLevel(logging.INFO)

        app_logger = logging.getLogger("app")
        app_logger.addHandler(cls.console_handler)
        app_logger.setLevel(logging.DEBUG)

        utils_logger = logging.getLogger("utils")
        utils_logger.addHandler(cls.console_handler)
        utils_logger.setLevel(logging.DEBUG)

        commands_logger = logging.getLogger("cmds")
        commands_logger.addHandler(cls.console_handler)
        commands_logger.setLevel(logging.DEBUG)

        logging.getLogger('discord.app_commands.tree').setLevel(logging.DEBUG)

        app_logger.debug("Logging successfully initialized")