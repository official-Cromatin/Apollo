import logging
import discord
from utils.interaction_handler.general_handler import General_Handler

class Button_Interaction_Handler(General_Handler):
    """Provides the possibility to link an interaction callback function of an cog, to an button interaction the bot recieves."""
    logger = logging.getLogger("utils.btnh")
    lookup_table:dict[str, complex] = {}

    @classmethod
    async def handle_interaction(cls, interaction: discord.Interaction):
        button_id = interaction.data["custom_id"]
        if button_id in cls.lookup_table:
            func = cls.lookup_table[button_id](interaction)
            cls.logger.debug(f"Interaction with button ({button_id}), handled by {func.__name__}")
            await func
        else:
            cls.logger.error(f"No handler for the button id {button_id} has been found")