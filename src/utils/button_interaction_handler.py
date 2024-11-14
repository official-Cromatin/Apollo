import discord
import logging
from functools import partial

class Button_Interaction_Handler():
    """Provides the possibility to link an interaction callback function of an cog, to an interaction the bot recieves.
    
    To work properly, the custom id of the button MUST start with the given prefix for the link function"""
    logger = logging.getLogger("utils.btnh")
    lookup_table:dict[str, complex] = {}

    @classmethod
    def __get_matching_keys(cls, button_id:str) -> list[str]:
        """Compares the prefixes of all known handlers, to the start of the button id"""
        matching_keys = []
        
        for prefix_key in cls.lookup_table:
            if button_id.startswith(prefix_key):
                matching_keys.append(prefix_key)
        return matching_keys

    @classmethod
    def link_button_callback(cls, prefix:str = "", instance = None):
        """Links an function to the handler, which will be called when the button recieves an interaction"""
        def decorator(func):
            if prefix == "":
                raise ValueError("Prefix must contain a valid prefix")
        
            if prefix in cls.lookup_table:
                cls.logger.warning(f"The handler for the {prefix} was overridden")
            
            cls.lookup_table[prefix] = func
            
            cls.logger.info(f"Linked the handler {func.__name__} with {prefix}")

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @classmethod
    def unlink_button_callback(cls, prefix:str = ""):
        """Unlinks an function to the handler, useful when the cog its bound to gets reloaded or unloaded after all"""
        if prefix == "":
            raise ValueError("Prefix must contain a valid prefix")
    
        if prefix in cls.lookup_table:
            function = cls.lookup_table.pop(prefix)
            cls.logger.info(f"Unlinked the handler {function.__name__} with {prefix}")
        else:
            cls.logger.warning(f"There is no handler saved for the prefix {prefix}! - Nothing has been done")
    
    @classmethod
    async def handle_interaction(cls, interaction: discord.Interaction):
        """Called when an interaction with an button happened and needs to be handled"""
        button_id = interaction.data["custom_id"]
        matching_keys = cls.__get_matching_keys(button_id)
        number_of_keys = len(matching_keys)
        if number_of_keys > 1:
            cls.logger.error(f"The button id ({button_id}), matches with multiple callback handlers ({' '.join(matching_keys).strip(' ')})")
        elif number_of_keys > 0:
            key = matching_keys[0]
            func = cls.lookup_table[key](interaction)
            cls.logger.debug(f"Interaction with button ({button_id}), handled by {func.__name__}")
            await func
        else:
            cls.logger.error(f"No handler for the button id {button_id} has been found")