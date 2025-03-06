from abc import ABC, abstractmethod
from asyncpg import Connection
from typing import Any

class Base_Model(ABC):
    """Base class from which all models must inherit, they specify the forced fundamental CRUD functions."""
    def __init__(self, database_connection:Connection):
        self._connection = database_connection
        self._id:int
    
    @abstractmethod
    def __str__(self) -> str:
        ...
    
    @abstractmethod
    @classmethod
    async def create(self, *args) -> "Base_Model":
        """Creates a new entry in the database"""
        ...

    @abstractmethod
    @classmethod
    async def load(self, *args) -> "Base_Model":
        """Loads an existing entry from the database"""
        ...
    
    @abstractmethod
    async def save(self):
        """Updates the saved data, regardless of whether the values have changed or not"""
        ...

    @abstractmethod
    async def delete(self):
        """Removes the entry from the table, the data in the properties of the object is retained"""
        ...

    @abstractmethod
    def arguments(self) -> dict[str, Any]:
        """Returns the arguments required to uniquely identify an entry in the database"""
        ...

    @abstractmethod
    def data(self) -> dict[str, Any]:
        """Returns the data that the entry stores in the database (excludes the arguments for unique identification)"""
        ...
