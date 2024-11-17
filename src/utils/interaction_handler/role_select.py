import logging
import discord
from utils.interaction_handler.general_handler import General_Handler

class RoleSelect_Interaction_Handler(General_Handler):
    """Provides the possibility to link an interaction callback function of an cog, to an role select menu interaction the bot recieves."""
    logger = logging.getLogger("utils.rsnh")
    lookup_table:dict[str, complex] = {}

    @classmethod
    async def handle_interaction(cls, interaction: discord.Interaction):
        role_select_id = interaction.data["custom_id"]
        if role_select_id in cls.lookup_table:
            func = cls.lookup_table[role_select_id](interaction)
            cls.logger.debug(f"Interaction with role select ({role_select_id}), handled by {func.__name__}")
            await func
        else:
            cls.logger.error(f"No handler for the role select {role_select_id} has been found")