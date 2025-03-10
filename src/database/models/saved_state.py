from database.models.base_model import Base_Model
from database.models.exceptions import NotFound, NoLongerExists, AlreadyExists
from asyncpg import Connection, UniqueViolationError
from datetime import datetime

class Saved_State(Base_Model):
    """
    Represents the state of a view that can be restored.
    
    Offers functions to save, load and delete the state.
    
    The data can be accessed via the displayed properties
    
    | Attribute name    | Mutability   | Description                                            |
    |-------------------|--------------|--------------------------------------------------------|
    | `channel_id`      | `read-only`  | ID of the channel the state is saved for               |
    | `guild_id`        | `read-only`  | ID of the guild the state is saved for                 |
    | `state`           | `read-only`  | Relevant data of the view to be restorable             |
    | `view_state`      | `read-only`  | State of the view                                      |
    | `creation_date`   | `read-only`  | Datetime the state was saved                           |
    """
    LOAD = ""
    SAVE = ""
    DELETE = ""

    def __init__(self, database_connection:Connection, channel_id:int, guild_id:int, state:dict, view_state:int, creation_date:datetime):
        super().__init__(database_connection)
        self.__channel_id = channel_id
        self.__guild_id = guild_id
        self.__state = state
        self.__view_state = view_state
        self.__creation_date = creation_date
    
    def __str__(self):
        return f"Saved_State({self.arguments()}, {self.data()})"
    
    @classmethod
    async def create(cls, database_connection:Connection, channel_id:int, guild_id:int, state:dict) -> "Saved_State":
        """Creates a new model with the specified data.
        
        :param Connection database_connection:
            Connection to the database used for later actions
        
        :param int channel_id:
            ID of the channel the state is saved for
            
        :param int guild_id:
            ID of the guild the state is saved for
            
        :param dict state:
            Relevant data of the view to be restorable
            
        :return:
            The created model
            
        :raises AlreadyExists:
            If the state is already saved for the specified channel and guild"""
        model = Saved_State(database_connection, channel_id, guild_id, state)
        await model.save()
        return model

    @classmethod
    async def load(cls, database_connection:Connection, channel_id:int, guild_id:int) -> "Saved_State":
        """Loads an existing model from the database.
        
        :param Connection database_connection:
            Connection to the database used for later actions
            
        :param int channel_id:
            ID of the channel the state is saved for
        
        :param int guild_id:
            ID of the guild the state is saved for
        
        :return:
            The loaded model
        
        :raises NotFound:
            If the state is not found for the specified channel and guild"""
        row = await database_connection.fetchrow(cls.LOAD, channel_id, guild_id)
        if row is None:
            raise NotFound("Saved_State", {"channel_id":channel_id, "guild_id":guild_id})
        return Saved_State(database_connection, row["channel_id"], row["guild_id"], row["state"], row["view_state"], row["creation_date"])
    
    async def save(self) -> "Saved_State":
        if self._deleted:
            raise NoLongerExists("Saved_State", self.arguments(), self.data())
        
        try:
            await self._connection.execute(self.SAVE, self.__channel_id, self.__guild_id, self.__state, self.__view_state, self.__creation_date)
        except UniqueViolationError:
            raise AlreadyExists("Saved_State", self.arguments())
        return self
    
    async def delete(self) -> "Saved_State":
        if self._deleted:
            raise NoLongerExists("Saved_State", self.arguments(), self.data())
        
        if await self._connection.fetchval(self.DELETE, self.__channel_id, self.__guild_id) is None:
            raise NotFound("Saved_State", self.arguments())
        self._deleted = True
        return self

    def arguments(self) -> dict:
        return {"channel_id": self.__channel_id, "guild_id": self.__guild_id}

    def data(self) -> dict:
        return {"state": self.__state, "view_state": self.__view_state, "creation_date": self.__creation_date}
    
    @property
    def channel_id(self) -> int:
        return self.__channel_id
    
    @property
    def guild_id(self) -> int:
        return self.__guild_id
    
    @property
    def state(self) -> dict:
        return self.__state
    
    @property
    def view_state(self) -> int:
        return self.__view_state
    
    @property
    def creation_date(self) -> datetime:
        return self.__creation_date
