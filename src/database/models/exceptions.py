from abc import abstractmethod, ABC
from typing import Any

class BaseModelException(Exception, ABC):
    """Used as the basis for all executions performed by operations on and with the models"""
    def __init__(self, model_name:str):
        self.name = model_name

    @abstractmethod
    def __str__(self):
        ...

    @staticmethod
    def keyword_to_string(keyword_arguments:dict[str, Any]) -> str:
        """Converts a dictionary of keyword arguments into a formatted string
        
        Example: 
        ---
        ```
        .keyword_to_string({"user_id": 815, "channel_id": 7411})
        ```
        
        Returns
        ```
        "user_id=815, channel_id=7411"
        ```"""
        return ", ".join(f"{key}={value}" for key, value in keyword_arguments.items())


class NotFound(BaseModelException):
    """The requested data was not found"""
    def __init__(self, model_name:str, arguments:dict[str, Any]):
        super().__init__(model_name)
        self.arguments = arguments

    def __str__(self):
        return f"Loading the data for model {self.name} failed, the data could not be found with the specified arguments ({self.keyword_to_string(self.arguments)})"


class AlreadyExists(BaseModelException):
    """The data already exists"""
    def __init__(self, model_name:str, arguments:dict[str, Any]):
        super().__init__(model_name)
        self.arguments = arguments

    def __str__(self):
        return f"Creating the data for model {self.name} failed, the data already exists with the specified arguments ({self.keyword_to_string(self.arguments)})"


class NoLongerExists(BaseModelException):
    """The entry no longer exists, manipulative operations (save, delete) fail"""
    def __init__(self, model_name:str, arguments:dict[str, Any], data:dict[str, Any]):
        super().__init__(model_name)
        self.arguments = arguments
        self.data = data

    def __str__(self):
        return f"Changing the saved data failed, the data ({self.keyword_to_string(self.arguments)}; {self.keyword_to_string(self.data)}) for model {self.name} could not be saved"


class InsufficientBalance(BaseModelException):
    """The user has insufficient balance"""
    def __init__(self, model_name:str, user_id:int, guild_id:int, balance:int, required:int):
        super().__init__(model_name)
        self.user_id = user_id
        self.guild_id = guild_id
        self.balance = balance
        self.required = required

    def __str__(self):
        return f"The user ({self.user_id}) has insufficient balance ({self.balance}) on the guild ({self.guild_id}), required ({self.required})"
