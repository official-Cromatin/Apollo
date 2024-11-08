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

# Import all the remaining dependencies
import discord
from discord.ext import commands
from pathlib import Path
from utils.portal import Portal
from utils.datetime_tools import get_elapsed_time_smal, get_elapsed_time_big
from utils.adv_configparser import Advanced_ConfigParser
import re
import traceback
import asyncio

source_path = Path(__file__).resolve()
base_path = source_path.parents[1]
app_logger.info(f"Using the following path as entrypoint: '{base_path}'")

class Apollo_Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        super().__init__(command_prefix=None, help_command=None, intents=intents)

        self.__portal:Portal

    def set_portal(self, portal:Portal):
        self.__portal = portal

    async def on_interaction(self, interaction: discord.Interaction):
        """Called when an interaction happened"""
        match interaction.type.name:
            case discord.InteractionType.application_command.name:
                print("Interaction with bot", interaction.command.name)
                self.__portal.no_executed_commands += 1
            case discord.InteractionType.ping.name:
                # print("App got pinged by discord")
                pass
            case discord.InteractionType.autocomplete.name:
                # print("Interaction with autocomplete")
                pass
            case discord.InteractionType.modal_submit.name:
                # print("Modal interaction submitted")
                pass
            case discord.InteractionType.component.name:
                # print("Component interaction")
                pass

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
