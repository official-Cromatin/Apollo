print("      ___    ____  ____  __    __    ____  ")
print("     /   |  / __ \/ __ \/ /   / /   / __ \ ")
print("    / /| | / /_/ / / / / /   / /   / / / / ")
print("   / ___ |/ ____/ /_/ / /___/ /___/ /_/ /  ")
print("  /_/  |_/_/    \____/_____/_____/\____/   ")
print("  Copyright (c) 2024-2025 Cromatin         ")
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
from pathlib import Path
from utils.datetime_tools import get_elapsed_time_big
from utils.adv_configparser import Advanced_ConfigParser
import re
import traceback
import asyncio
import sys
from bot import Apollo_Bot

source_path = Path(__file__).resolve()
base_path = source_path.parents[1]
app_logger.info(f"Using the following path as entrypoint: '{base_path}'")
PROGRAM_VERSION = "0.3"

# Create bot instance
bot = Apollo_Bot(base_path, startup_time, PROGRAM_VERSION)
bot_config = Advanced_ConfigParser(Path.joinpath(base_path, "config", "bot.ini"))
if re.match(r'[A-Za-z\d]{24}\.[\w-]{6}\.[\w-]{27}', bot_config["DISCORD"]["TOKEN"]):
    app_logger.critical("Bot (config/bot.ini) configuration invalid, please set a valid token")
    quit(1)
elif bot_config.compare_to_template() not in ("equal", "config_minus"):
    app_logger.critical("Bot (config/bot.ini) configuration is missing some parts. Make sure it at least has all the same keys as the template")
    quit(1)
else:
    app_logger.info("Bot configuration valid, continuing with startup")

# Setup handlers to handle states of command execution
@bot.tree.error
async def on_app_command_error(ctx:discord.Interaction, error):
    """Executed when exception during command execution occurs"""
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__)

try:
    bot.run(bot_config["DISCORD"]["TOKEN"], log_handler = None)
except discord.errors.LoginFailure:
    app_logger.critical("Improper token has been passed. Aborting startup")
    quit(1)

app_logger.info("Quitting application ...")
asyncio.run(bot.close())
app_logger.info(f"Exiting. Application ran for {get_elapsed_time_big(datetime.now().timestamp() - startup_time)}")
