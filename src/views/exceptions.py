from abc import abstractmethod
from typing import Any

class GeneralViewException(Exception):
    """Base class for all exceptions, encounterd when using the restorable view"""
    def __init__(self, view_name:str):
        """
        :param str view_name:
            Name of the view class"""
        self.name = view_name

    @abstractmethod
    def __str__(self):
        ...

    @staticmethod
    def keyword_to_string(keyword_arguments:dict[str, Any]) -> str:
        """Converts a dictionary of keyword arguments into a formatted string

        :param dict keyword_arguments:
            Dictionary with keys as attribute names and thier respektive value

        :return str:
            Formatted data with `key=value key2=value2 ...`
        
        Example: 
        ---
        ```
        >>> keyword_to_string({"user_id": 815, "channel_id": 7411})
        "user_id=815, channel_id=7411"
        ```
        `"""
        return ", ".join(f"{key}='{value}'" for key, value in keyword_arguments.items())


class GeneralAttributeException(GeneralViewException):
    """Base class for all exceptions, beling related with attributes"""
    def __init__(self, view_name:str, attribute_name:str):
        """
        :param str view_name:
            Name of the view class

        :param str attribute_name:
            Name of the attribute involved"""
        super().__init__(view_name)
        self.attribute_name = attribute_name


class GeneralExtendedViewException(GeneralViewException):
    """Extended base class all exceptions inherit, used when more data"""
    def __init__(self, view_name:str, attributes:dict[str, Any]):
        """
        :param str view_name:
            Name of the view class

        :param dict attributes:
            All attributes the view has"""
        super().__init__(view_name)
        self.attributes = attributes


class GeneralStoredViewException(GeneralExtendedViewException):
    """Base class specific to all exceptions, being thrown in combination with stored data by the database"""
    def __init__(self, view_name:str, attributes:dict[str, Any], database_id:int):
        """
        :param str view_name:
            Name of the view class

        :param int | None database_id:
            ID of the row in the database table, can be None if no state is saved

        :param dict attributes:
            All attributes the view has"""
        super().__init__(view_name, attributes)
        self.database_id = database_id


class AlreadyStopped(GeneralStoredViewException):
    """Stopped view was requested to stop"""
    def __str__(self):
        return f"Attempt was made to stop view '{self.name}' that was stopped, database_id={self.database_id} and attributes {self.keyword_to_string(self.attributes)}"


class StoppedBefore(GeneralStoredViewException):
    """View has been stopped but is now requested to start"""
    def __str__(self):
        return f"Tried to start view '{self.name}' that was stopped before, database_id={self.database_id} and attributes {self.keyword_to_string(self.attributes)}"


class AlreadyActive(GeneralStoredViewException):
    """Activated view was requested to activate"""
    def __str__(self):
        return f"Attempt was made to start view '{self.name}' that was started, database_id={self.database_id} and attributes {self.keyword_to_string(self.attributes)}"


class NotActive(GeneralStoredViewException):
    """Inactive view was requested to stop"""
    def __str__(self):
        return f"Attempt was made to stop view '{self.name}' that was never started, database_id={self.database_id} and attributes {self.keyword_to_string(self.attributes)}"


class CallbackNotFound(GeneralViewException):
    """No callback for the id was found"""
    def __init__(self, view_name:str, custom_id:str):
        """
        :param str view_name:
            Name of the view class

        :param str custom_id:
            Custom id requested that could not be found"""
        super().__init__(view_name)
        self.custom_id = custom_id

    def __str__(self):
        return f"The callback for the view '{self.name}' with the custom id '{self.custom_id}' was not found"


class AttributeNameConflict(GeneralAttributeException):
    """Attribute with same name was saved already"""
    def __str__(self):
        return f"While getting the attributes for the view '{self.name}', the value for the already saved attribute '{self.attribute_name}' was about to be overridden"


class AttributeNotFound(GeneralAttributeException):
    """Non-existent attribute was tried to set"""
    def __str__(self):
        return f"While restoring the attributes for the view '{self.name}', a non-existing attribute '{self.attribute_name}' was tried to be set"


class MessageIdMissing(GeneralViewException):
    def __str__(self):
        return f"Activation of view '{self.name}' failed, no message id set"
