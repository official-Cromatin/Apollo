import discord
import logging
from functools import partial
from abc import ABC, abstractmethod

class General_Handler(ABC):
    """Provides the possibility to link an interaction callback function of an cog, to an interaction the bot recieves.
    
    The handle_interaction classfunction must be implemented, the General_Handler CANNOT be used directly!"""
    logger: logging.Logger
    lookup_table:dict[str, complex] = {}

    @classmethod
    def link_button_callback(cls, custom_id:str = "", instance = None):
        """Links an function to the handler, which will be called when the button recieves an interaction"""
        def decorator(func):
            if custom_id == "":
                raise ValueError(f"custom_id must contain a valid value, not '{custom_id}'")
        
            if custom_id in cls.lookup_table:
                cls.logger.warning(f"The handler for the {custom_id} was overridden")
            
            cls.lookup_table[custom_id] = func
            
            cls.logger.info(f"Linked the handler {func.__name__} with {custom_id}")

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @classmethod
    def unlink_button_callback(cls, custom_id:str = ""):
        """Unlinks an function to the handler, useful when the cog its bound to gets reloaded or unloaded after all"""
        if custom_id == "":
            raise ValueError(f"custom_id must contain a valid value, not '{custom_id}'")
    
        if custom_id in cls.lookup_table:
            function = cls.lookup_table.pop(custom_id)
            cls.logger.info(f"Unlinked the handler {function.__name__} with {custom_id}")
        else:
            cls.logger.warning(f"There is no handler saved for the custom_id {custom_id}! - Nothing has been done")
    
    @classmethod
    @abstractmethod
    async def handle_interaction(cls, interaction: discord.Interaction):
        """Called when an interaction happened and needs to be handled"""