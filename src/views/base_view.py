import discord
from abc import ABC
from bot import Apollo_Bot
from typing import Any, Union, Callable
from views.exceptions import AlreadyActive, StoppedBefore, AlreadyStopped, NotActive, CallbackNotFound, AttributeNameConflict, AttributeNotFound, MessageIdMissing
from database.models.saved_state.model import Saved_State
from database.models.saved_state.model import View_Names
import logging

class Base_View(discord.ui.View, ABC):
    """Base class wich all views have to inherit
    
    To create a restorable view, you have to implement the following methods:
    | Function name         | Optional   | Description                                                      |
    |-----------------------|------------|------------------------------------------------------------------|
    | `new`                 | `false`    | Creates a new view and sets the view specific attributes         |
    | `restore`             | `true`     | Restores a existing view, restoring the values of all attributes |
    | `save_state`          | `true`     | Saves the state (values of the attributes) of the view           |
    | `identify_callback`   | `true`     | Identified the matching callback, based on the custom_id         |
    """
    _view_name:View_Names = None

    def __init_subclass__(cls, view_name:View_Names):
        cls._view_name = view_name
    
    def __init__(self, guild_id:int, channel_id:int, original_interaction_id:int, bot:"Apollo_Bot", timeout = 180):
        """
        :param int guild_id:
            ID of the Discord guild the view is created in

        :param int channel_id:
            ID of the Discord channel the view is created in

        :param int original_interaction_id:
            ID of the interaction that triggered the creation of the view

        :param Apollo_Bot bot:
            Instance of the bot the view was created with

        :param int timeout:
            Time in seconds, after wich the view will be saved in the database and removed from memory
        """
        super().__init__(timeout=timeout)
        self._original_interaction_id = original_interaction_id
        self._bot = bot
        self._stopped = False
        self._saved_state = Saved_State.create(bot.new_database, guild_id, channel_id, None, None, self._view_name, timeout)
        self._view_data_attribute_names:list[str] = []

    def new(self, *args, **kwargs) -> "Base_View":
        """Creates a new view, responsible for setting all initial values"""
        logging.getLogger("view").info(f"New view (timeout={self.timeout}) created on guild {self._saved_state.guild_id} in channel {self._saved_state.channel_id} iniated by interaction {self._original_interaction_id}", extra={"iname": self._view_name.value})

    def set_message_id(self, message_id:int):
        """
        :param int message_id:
            ID of the Discord message the view belongs to"""
        self._saved_state.message_id = message_id
        logging.getLogger("view").info(f"Set message id {self._saved_state.message_id} for view originaly initiated by interaction {self._original_interaction_id}", extra={"iname": self._view_name.value, "id": self._saved_state.message_id})

    def restore(self, state:Saved_State, message:discord.Message) -> "Base_View":
        """Restores a existing view from the given state

        *Note: The restore of all attributes and ui components*

        Warning: If the custom_id of the element has no matching function, the reconstruction for this component will fail!
        
        :param Saved_State state:
            Saved state model containing saved data
            
        :param discord.Message message:
            Message object from the interaction
            
        :param Apollo_Bot bot:
            Bot instance"""
        # Restore the ui components themself
        action_row_number = 0
        for action_row in message.components:
            for component in action_row.children:

                # Attempt to restore the callback
                try:
                    callback = self.identify_callback(component.custom_id)
                except CallbackNotFound:
                    logging.getLogger("view").error(f"Failed to restore callback for ui element with custom_id={restored_component.custom_id}!", extra={"iname": state.view_name, "id": state.message_id})

                # Restore component and add to view
                restored_component = self.restore_component(component, callback, action_row_number)
                self.add_item(restored_component)
            action_row_number += 1

        # Restore the saved attributes
        self.set_attributes(state.state_data)

        self._saved_state = state
        logging.getLogger("view").info(f"Existing view (timeout={self.timeout}) restored on guild ({state.guild_id}) in channel {state.channel_id}", extra={"iname": state.view_name, "id": state.message_id})
        return self

    async def save_state(self):
        """Saves the state the view is currently in
        
        Note: It respects ONLY attributes specified in `_view_data` (name mangling must not be accounted for)"""
        view_data = self.get_attributes(self._view_data_attribute_names)

        # If no attributes are set, insert NULL in the column as a representation of no values being specified
        if len(view_data) == 0:
            view_data = None
        
        # Update saved data
        self._saved_state.state_data = view_data
        await self._saved_state.save()
        
        logging.getLogger("view").debug(f"Saved view", extra={"iname": self._view_name.value, "id": self._saved_state.message_id})

    def identify_callback(self, custom_id:str) -> Callable:
        """Returns the callback method for the matching custom_id

        Override if you have custom_ids that dont match the name of the callback function BEFORE calling this super function
        
        :param str custom_id:
            Custom id specified at the creation of the ui element
            
        :return Callable:
            Matching function for the given `custom_id`
        
        :raise CallbackNotFound:
            The requested `custom_id` is unknown to this view
        """
        if hasattr(self, custom_id):
            callback = getattr(self, custom_id)
            if callable(callable):
                return callback

        if self._saved_state is None:
            raise CallbackNotFound(self._view_name.value, custom_id)
        raise CallbackNotFound(self._view_name.value, custom_id)

    def get_attributes(self, filter:list[str] = None, unmangle_attribute_name:bool = False) -> dict[str, Any]:
        """Returns the view specific attributes, as defined in `view_data_attribute_names`
        
        :param list[str] filter:
            If specified, only attributes that are specified by name are stored in the Dict

            Warning: If unmangling is deactivated, the attribute name must be mangled

        :param unmangle_attribute_name bool:
            The attribute names in the dict will be unmangled (Might lead to conflics and might not be restorable)

        :raise AttributeNameConflict:
            An attribute with the same name has already been saved in the dict.

            *Note: This can be prevented by `unmangle_attribute_name` = `False`*

        :return:
            Dictionary containing the names of the attributes and its respective value"""
        view_data:Union[dict[str, Any] | None] = {}
        for cls in self.__class__.mro():
            if cls is object:
                continue

            class_name = cls.__name__
            for attr in self.__dict__:
                value = getattr(self, attr)

                # Unmangle attribute_name
                if unmangle_attribute_name:
                    if attr.startswith(f"_{class_name}__"):
                        attribute_name = attr.removeprefix(f"_{class_name}__")
                    else:
                        attribute_name = attr
                else:
                    if attr.startswith(f"_{class_name}__"):
                        short_name = attr.removeprefix(f"_{class_name}__")
                        attribute_name = f"{class_name}.__{short_name}"
                    else:
                        attribute_name = f"{class_name}.{attr}"

                if filter is None or attribute_name not in filter:
                    continue

                if attribute_name in view_data:
                    raise AttributeNameConflict(self._view_name.value, attribute_name)
                view_data[attribute_name] = value
        return view_data

    def set_attributes(self, attribute_data:dict[str, Any]):
        """Restores the value of the attributes specified in the dictionary

        *Note: Only unmangled values will function properly*
        
        :param dict[str, Any] attribute_data:
            The values of the attributes to be restored"""
        for attribute_name, attribute_value in attribute_data.items():
            if ".__" in attribute_name:
                # Remangle: Sub.__foo -> _Sub__foo
                class_name, short_name = attribute_name.split(".__", maxsplit=1)
                mangled_name = f"_{class_name}__{short_name}"
            elif "." in attribute_name:
                # Regular: Base.foo -> foo (set as-is)
                _, mangled_name = attribute_name.split(".", maxsplit=1)
            else:
                # Already unmangled, use as-is
                mangled_name = attribute_name

            if hasattr(self, mangled_name):
                setattr(self, mangled_name, attribute_value)
            else:
                raise AttributeNotFound(self._view_name.value, attribute_name)

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

        :raises TypeError:
            Tried to restore a unsupported component
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
        if self._saved_state.active:
            raise AlreadyActive(self._view_name.value, self.get_attributes(unmangle_attribute_name = True), self._saved_state.id,)
        if self._stopped:
            raise StoppedBefore(self._view_name.value, self.get_attributes(unmangle_attribute_name = True), self._saved_state.id,)
        if self._saved_state.message_id is None:
            raise MessageIdMissing(self._view_name.value)
        self._bot.active_views[self._saved_state.message_id] = self
        self._saved_state.active = True

    def deactivate(self):
        """Deactivates the view, removing it from the list of all active views
        
        :raises AlreadyStopped:
            View was stopped before
            
        :raises NotActive:
            View was never started
        """
        if self._stopped:
            raise AlreadyStopped(self._view_name.value, self.get_attributes(unmangle_attribute_name = True), self._saved_state.id,)
        if not self._saved_state.active:
            raise NotActive(self._view_name.value, self.get_attributes(unmangle_attribute_name = True), self._saved_state.id)
        del self._bot.active_views[self._saved_state.message_id]
        self._saved_state.active = False
        self._stopped = True
    
    async def stop(self):
        logging.getLogger("view").info("View was stopped", extra={"iname": self._view_name.value, "id": self._saved_state.message_id})
        self.deactivate()
        super().stop()
        await self.save_state()

    async def on_timeout(self):
        logging.getLogger("view").info("View has expired", extra={"iname": self._view_name.value, "id": self._saved_state.message_id})
        self.deactivate()
        await super().on_timeout()
        await self.save_state()

    @property
    def view_name(self) -> View_Names:
        """View_Name enum member"""
        return self._view_name
