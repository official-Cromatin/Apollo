from abc import ABC, abstractmethod
from asyncpg import Connection
from typing import Any

class Base_Model(ABC):
    """Base class from which all models must inherit, they specify the forced fundamental CRUD functions."""
    def __init__(self, database_connection:Connection, id:int):
        self._connection = database_connection
        self._id = id
        self._saved = False
        self._deleted = False
    
    @abstractmethod
    def __str__(self) -> str:
        ...
    
    @classmethod
    @abstractmethod
    async def create(cls, *args) -> "Base_Model":
        """Creates a new entry in the database
        
        :return:
            An instance of User_Currency with the specified data
        
        :raises AlreadyExists:
            If the user currency already exists in the database"""
        ...

    @classmethod
    @abstractmethod
    async def load(cls, *args) -> "Base_Model":
        """Loads an existing entry from the database
        
        :return: 
            An instance of User_Currency with the loaded data
        
        :raises NotFound:
            If the user currency is not found in the database"""
        ...
    
    @abstractmethod
    async def save(self) -> "Base_Model":
        """Updates the saved data, regardless of whether the values have changed or not

        :returns self:
            The object itself, to allow for chaining

        :raises AlreadyExists:
            The entry already exists

        :raises NoLongerExists:
            The entry has been deleted
        """
        ...

    @abstractmethod
    async def delete(self) -> "Base_Model":
        """Removes the entry from the table, the data in the properties of the object is retained
        
        :returns self:
            The object itself, to allow for chaining
        
        :raises NoLongerExists:
            The entry has already been deleted

        :raises NotFound:
            The entry has not been found
        """
        ...

    @abstractmethod
    def arguments(self) -> dict[str, Any]:
        """Returns the arguments required to uniquely identify an entry in the database"""
        ...

    @abstractmethod
    def data(self) -> dict[str, Any]:
        """Returns the data that the entry stores in the database (excludes the arguments for unique identification)"""
        ...
    
    @property
    def id(self) -> int | None:
        """Unique identifier (primary key) of the entry, None if not saved"""
        return self._id
    
    @property
    def saved(self) -> bool:
        """Indicates whether the entry has been ever saved"""
        return self._saved

    @property
    def deleted(self) -> bool:
        """Indicates whether the entry has been deleted"""
        return self._deleted
