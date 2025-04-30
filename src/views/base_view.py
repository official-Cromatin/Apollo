import discord
from abc import ABC, abstractmethod
from bot import Apollo_Bot
from typing import Any, Union, Callable
from views.exceptions import AlreadyActive, StoppedBefore, AlreadyStopped, NotActive
from database.models.saved_state import Saved_State
import logging

class Base_View(discord.ui.View, ABC):
    """Base class wich all views have to inherit"""
    _view_name:str = None

    def __init_subclass__(cls, view_name:str):
        cls._view_name = view_name
    
    def __init__(self, guild_id:int, channel_id:int, message_id:int, bot:Apollo_Bot, timeout = 180):
        """
        :param int guild_id:
            ID of the Discord guild the view is created in

        :param int channel_id:
            ID of the Discord channel the view is created in

        :param int message_id:
            ID of the Discord message the view belongs to

        :param Apollo_Bot bot:
            Instance of the bot the view was created with

        :param int timeout:
            Time in seconds, after wich the view will be saved in the database and removed from memory
        """
        super().__init__(timeout=timeout)
        self._guild_id = guild_id
        self._channel_id = channel_id
        self._message_id = message_id
        self._bot = bot
        self._active:bool = False
        self._stopped:bool = False
        self._database_id:int = None

    def new(self, *args, **kwargs) -> "Base_View":
        """Creates a new view, responsible for setting all initial values"""
        logging.getLogger("view").info(f"New view (timeout={self.timeout}) created on guild {self._guild_id} in channel {self._channel_id}", extra={"iname": self._view_name, "id": self._message_id})

    def restore(state:Saved_State, message:discord.Message) -> "Base_View":
        """Restores a existing view from the given state"""
        logging.getLogger("view").info(f"Existing view restored on guild ({state.guild_id}) in channel {state.channel_id}", extra={"iname": state.view_name, "id": state.message_id})

    @abstractmethod
    def identify_callback(self, custom_id:str) -> function:
        """Returns the callback method for the matching custom_id
        
        :param str custom_id:
            Custom id specified at the creation of the ui element
            
        :return function:
            Matching function for the given `custom_id`
        
        :raise CallbackNotFound:
            The requested `custom_id` is unknown to this view
        """
        ...

    async def save_state(self):
        """Saves the state the view is currently in"""
        logging.getLogger("view").debug(f"Saved view")

    @staticmethod
    def restore_component(component:Union[discord.Button, discord.SelectMenu, discord.TextInput], callback:Callable, row:int = None) -> Union[discord.ui.Button, discord.ui.Select, discord.ui.UserSelect, discord.ui.RoleSelect, discord.ui.MentionableSelect, discord.ui.TextInput]:
        """Restores the given `component` as a discord.ui element
        
        :param discord.Button | discord.SelectMenu | discord.TextInput component:
            Component that has to be restored

        :param Callable callback:
            Function to callback when the user interacts with the ui element

        :param int row:
            Row to place the button in
        
        :return discord.ui.Button | discord.ui.Select | discord.ui.UserSelect | discord.ui.RoleSelect | discord.ui.TextInput:
            Restored discord.ui element
        """
        element: Union[discord.ui.Button, discord.ui.Select, discord.ui.UserSelect, discord.ui.RoleSelect, discord.ui.MentionableSelect, discord.ui.TextInput]
        match component.type:
            case discord.ComponentType.button:
                element = discord.ui.Button(
                    style = component.style,
                    label = component.label,
                    disabled = component.disabled,
                    custom_id = component.custom_id,
                    url = component.url,
                    emoji = component.emoji,
                    row = row,
                    sku_id = component.sku_id
                )

            case discord.ComponentType.string_select:
                element = discord.ui.Select(
                    custom_id = component.custom_id,
                    placeholder = component.placeholder,
                    min_values = component.min_values,
                    max_values = component.max_values,
                    options = component.options,
                    disabled = component.disabled,
                    row = row
                )

            case discord.ComponentType.user_select | discord.ComponentType.role_select | discord.ComponentType.mentionable_select:
                Select_Class: type
                match component.type:
                    case discord.ComponentType.user_select:
                        Select_Class = discord.ui.UserSelect
                    case discord.ComponentType.role_select:
                        Select_Class = discord.ui.RoleSelect
                    case discord.ComponentType.mentionable_select:
                        Select_Class = discord.ui.MentionableSelect
                        
                element = Select_Class(
                    custom_id = component.custom_id,
                    placeholder = component.placeholder,
                    min_values = component.min_values,
                    max_values = component.max_values,
                    disabled = component.disabled,
                    row = row,
                    default_values = component.default_values
                )
            
            case discord.ComponentType.text_input:
                element = discord.ui.TextInput(
                    label = component.label,
                    style = component.style,
                    custom_id = component.custom_id,
                    placeholder = component.placeholder,
                    default = component.default_values,
                    required = component.required,
                    min_length = component.min_length,
                    max_length = component.max_length,
                    row = row
                )

            case _:
                raise TypeError(f"Invalid type of discord component (type={type(component)})")
        element.callback = callback
        return element
    
    def activate(self):
        """Activates the view, adding it to a list of all active views
        
        :raises AlreadyActive:
            View was activated before
            
        :raises StoppedBefore:
            View was stopped before but is now requested to start"""
        if self._active:
            raise AlreadyActive(self._view_name, self._database_id, self.get_attributes())
        if self._stopped:
            raise StoppedBefore(self._view_name, self._database_id, self.get_attributes())
        self._bot.active_views[self._message_id] = self
        self._active = True

    def deactivate(self):
        """Deactivates the view, removing it from the list of all active views
        
        :raises AlreadyStopped:
            View was stopped before
            
        :raises NotActive:
            View was never started
        """
        if self._stopped:
            raise AlreadyStopped(self._view_name, self._database_id, self.get_attributes())
        if not self._active:
            raise NotActive(self._view_name, self._database_id, self.get_attributes())
        del self._bot.active_views[self._message_id]
        self._active = False
        self._stopped = True
    
    async def stop(self):
        logging.getLogger("view").info("View was stopped")
        self.deactivate()
        super().stop()
        await self.save_state()

    async def on_timeout(self):
        logging.getLogger("view").info("View has expired")
        self.deactivate()
        await super().on_timeout()
        await self.save_state()

    def get_attributes(self) -> dict[str, Any]:
        """Returns all attributes set by this class and its parents
        
        :returns dict:
            Dictionary containing all attributes with its key"""
        result:dict[str, Any] = {}

        # Traverse the class hierarchy (Method Resolution Order)
        for cls in self.__class__.mro():
            if cls is object:
                continue  # Skip the base object class

            class_name = cls.__name__

            # Loop through all attributes stored directly on the instance
            for attr in self.__dict__:
                value = getattr(self, attr, None)

                # Handle private attributes (name-mangled): __attr -> _Class__attr
                if attr.startswith(f"_{class_name}__"):
                    unmangled = attr.removeprefix(f"_{class_name}__")
                    result[f"{class_name}.__{unmangled}"] = value

                # Handle protected attributes: _attr
                elif attr.startswith('_') and not attr.startswith('__'):
                    result[f"{class_name}._{attr.lstrip('_')}"] = value

                # Handle public attributes
                else:
                    result[f"{class_name}.{attr}"] = value

        return result
