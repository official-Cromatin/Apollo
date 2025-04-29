from abc import abstractmethod
from typing import Any

class GeneralViewException(Exception):
    """Base class all exceptions during saving or restoring might throw"""
    def __init__(self, view_name:str, database_id:int, attributes:dict[str, Any]):
        """
        :param str view_name:
            Name of the view class
        
        :param int | None database_id:
            ID of the row in the database table, can be None if no state is saved

        :param dict attributes:
            All attributes the view has"""
        self.name = view_name
        self.database_id = database_id
        self.attributes = attributes

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


class AlreadyStopped(GeneralViewException):
    """Stopped view was requested to stop"""
    def __str__(self):
        return f"Attempt was made to stop view '{self.name}' that was stopped, database_id={self.database_id} and attributes {self.keyword_to_string(self.attributes)}"


class StoppedBefore(GeneralViewException):
    """View has been stopped but is now requested to start"""
    def __str__(self):
        return f"Tried to start view '{self.name}' that was stopped before, database_id={self.database_id} and attributes {self.keyword_to_string(self.attributes)}"


class AlreadyActive(GeneralViewException):
    """Activated view was requested to activate"""
    def __str__(self):
        return f"Attempt was made to start view '{self.name}' that was started, database_id={self.database_id} and attributes {self.keyword_to_string(self.attributes)}"


class NotActive(GeneralViewException):
    """Inactive view was requested to stop"""
    def __str__(self):
        return f"Attempt was made to stop view '{self.name}' that was never started, database_id={self.database_id} and attributes {self.keyword_to_string(self.attributes)}"


class CallbackNotFound(GeneralViewException):
    """No callback for the id was found"""
    def __init__(self, view_name, database_id, attributes, custom_id:str):
        """
        :param str view_name:
            Name of the view class
        
        :param int | None database_id:
            ID of the row in the database table, can be None if no state is saved

        :param dict attributes:
            All attributes the view has
            
        :param str custom_id:
            Custom id requested that could not be found"""
        super().__init__(view_name, database_id, attributes)
