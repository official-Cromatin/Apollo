from discord.ext import commands
import logging

class Base_GroupCog(commands.GroupCog):
    def __init__(self, logger:logging.Logger):
        self._logger = logger

    async def cog_load(self):
        self._logger.debug(f"Group cog for the '{self.__class__.__name__}' command got loaded")

    async def cog_unload(self):
        self._logger.debug(f"Group cog for the '{self.__class__.__name__}' command got unloaded")