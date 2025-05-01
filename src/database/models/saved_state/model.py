from database.models.base_model.base_model import Base_Model
from database.models.base_model.exceptions import NotFound, NoLongerExists, AlreadyExists
from asyncpg import Connection, UniqueViolationError
from datetime import datetime
from database.models.saved_state.enum import View_Names
from bot import Apollo_Bot


class Saved_State(Base_Model):
    """
    Represents the state of a view that can be restored.
    
    Offers functions to save, load and delete the state.
    
    The data can be accessed via the displayed properties
    
    | Attribute name    | Mutability   | Description                                            |
    |-------------------|--------------|--------------------------------------------------------|
    | `id`              | `read-only`  | ID of the row in the database                          |
    | `guild_id`        | `read-only`  | ID of the guild the state is saved for                 |
    | `channel_id`      | `read-only`  | ID of the channel the state is saved for               |
    | `message_id`      | `read-only`  | ID of the messsage the state belongs to                |
    | `data`            | `read-write` | Relevant data of the view to be restorable             |
    | `view_name`       | `read-only`  | Enum member of the View_Names                          |
    | `timeout`         | `read-only`  | Number of seconds after the view will expire           |
    | `active`          | `read-only`  | Indicate if the view is currently loaded               |
    | `creation_date`   | `read-only`  | Datetime at wich the save was created the first time   |
    | `last_loaded`     | `read-only`  | Datetime at wich the save was last loaded              |
    | `last_updated`    | `read-only`  | Datetime at wich the save was last updated             |
    """
    LOAD = ""
    SAVE = ""
    DELETE = ""

    def __init__(self, database_connection:Connection, id:int, guild_id:int, channel_id:int, message_id:int, data:dict, view_name:View_Names, timeout:int, creation_date:datetime, last_loaded:datetime, last_updated:datetime):
        super().__init__(database_connection, id)
        self.__guild_id = guild_id
        self.__channel_id = channel_id
        self.__message_id = message_id
        self.__data = data
        self.__view_name = view_name
        self.__timeout = timeout
        self.__creation_date = creation_date
        self.__last_loaded = last_loaded
        self.__last_updated = last_updated
    
    def __str__(self):
        return f"Saved_State({self.arguments()}, {self.data()})"
    
    @classmethod
    def create(cls, database_connection:Connection, guild_id:int, channel_id:int, message_id:int, data:dict, view_name:str, timeout:int) -> "Saved_State":
        """Creates a new model with the specified data.

        :param Connection database_connection:
            Connection to the database

        :param int guild_id:
            ID of the guild the state is saved for

        :param int channel_id:
            ID of the channel the state is saved for

        :param int message_id:
            ID of the message the state belongs to

        :param dict data:
            Relevant data of the view to be restorable

        :param str view_name:
            Name of the view the data is saved for

        :param int timeout:
            Number of seconds after the view will expire

        :return:
            The created model"""
        model = Saved_State(database_connection, None, guild_id, channel_id, message_id, data, view_name, timeout, datetime.now(), None, None)
        return model

    @classmethod
    async def load(cls, database_connection:Connection, guild_id:int, channel_id:int, message_id:int) -> "Saved_State":
        """Loads an existing model from the database.
        
        :param Connection database_connection:
            Connection to the database
            
        :param int guild_id:
            ID of the guild the state is saved for

        :param int channel_id:
            ID of the channel the state is saved for
        
        :param int message_id:
            ID of the message the state belongs to
            
        :return:
            The loaded model
        
        :raises NotFound:
            If the state is not found for the specified channel and guild"""
        row = await database_connection.fetchrow(cls.LOAD, guild_id, channel_id, message_id, datetime.now())
        if row is None:
            raise NotFound("Saved_State", {"guild_id": guild_id, "channel_id": channel_id, "message_id": message_id})
        return Saved_State(database_connection, row["id"], guild_id, channel_id, message_id, row["data"], row["view_name"], row["timeout"], row["creation_date"], row["last_loaded"], row["last_updated"])

    async def save(self) -> "Saved_State":
        if self._deleted:
            raise NoLongerExists("Saved_State", self.arguments(), self.data())
        
        try:
            self._id = await self._connection.fetchval(self.SAVE, self.__guild_id, self.__channel_id, self.__message_id, self.__data, self.__view_name, self.__timeout, self.__creation_date, self.__last_loaded, self.__last_updated)
        except UniqueViolationError:
            raise AlreadyExists("Saved_State", self.arguments())
        self._saved = True
        return self

    async def delete(self) -> "Saved_State":
        if self._deleted:
            raise NoLongerExists("Saved_State", self.arguments(), self.data())
        
        if await self._connection.fetchval(self.DELETE, self.__guild_id, self.__channel_id, self.__message_id) is None:
            raise NotFound("Saved_State", self.arguments())
        self._deleted = True
        return self

    def arguments(self) -> dict:
        return {"guild_id": self.__guild_id, "channel_id": self.__channel_id, "message_id": self.__message_id}

    def data(self) -> dict:
        return {"data": self.__data, "view_name": self.__view_name.name, "timeout" : self.__timeout, "creation_date": self.__creation_date}

    @property
    def guild_id(self) -> int:
        """ID of the guild the state is saved for"""
        return self.__guild_id

    @property
    def channel_id(self) -> int:
        """ID of the channel the state is saved for"""
        return self.__channel_id

    @property
    def message_id(self) -> int:
        """ID of the messsage the state belongs to"""
        return self.__message_id

    @property
    def data(self) -> dict:
        """Relevant data of the view to be restorable"""
        return self.__data

    @property
    def view_name(self) -> View_Names:
        """Enum member of the View_Names"""
        return self.__view_name

    @property
    def timeout(self) -> int:
        """Number of seconds after the view will expire"""
        return self.__timeout

    @property
    def creation_date(self) -> datetime:
        """Datetime at wich the save was created"""
        return self.__creation_date
    
    @property
    def last_loaded(self) -> datetime:
        """Datetime at wich the save was last loaded"""
        return self.__last_loaded

    @property
    def last_updated(self) -> datetime:
        """Datetime at wich the save was last updated"""
        return self.__last_updated


async def setup(bot:Apollo_Bot):
    Saved_State.SAVE = await bot.sql_loader.get_file("dml.saved_state.create_new")
    Saved_State.LOAD = await bot.sql_loader.get_file("dml.saved_state.load_by_specific")
    Saved_State.DELETE = await bot.sql_loader.get_file("dml.saved_state.delete_by_specific")
