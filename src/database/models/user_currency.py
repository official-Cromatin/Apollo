from database.models.base_model import Base_Model
from database.models.exceptions import NotFound, AlreadyExists, NoLongerExists, InsufficientBalance
from asyncpg import Connection, UniqueViolationError
from datetime import datetime

class User_Currency(Base_Model):
    """
    Represents the assets of a user.

    Offers functions to manipulate the amount of assets (credit, deduct, check) 

    The data can be accessed via the displayed properties

    | Attribute name  | Mutability   | Description                                      |
    |-----------------|--------------|--------------------------------------------------|
    | `user_id`       | `read-only`  | ID of the user who owns the currency             |
    | `guild_id`      | `read-only`  | ID of the guild the user owns the currency on    |
    | `last_claimed`  | `read-only`  | Datetime the user has last claimed his dailymoney|
    | `currency`      | `read-write` | Current user balance                             |
    """
    LOAD = ""
    SAVE = ""
    DELETE = ""
    
    def __init__(self, database_connection, user_id:int, guild_id:int, last_claimed:datetime, currency:int):
        super().__init__(database_connection)
        self.__user_id = user_id
        self.__guild_id = guild_id
        self.__last_claimed = last_claimed
        self.__currency = currency

    @classmethod
    async def create(cls, database_connection:Connection, user_id:int, guild_id:int, currency:int) -> "User_Currency":
        """Creates a new model with the specified data.

        :param Connection database_connection: 
            Connection to the database used for later actions
            
        :param int user_id:
            ID of the user who owns the currency
        
        :param int guild_id:
            ID of the guild the user owns the currency on
        
        :param int currency:
            Initial currency balance
            
        :return:
            An instance of User_Currency with the specified data
        
        :raises AlreadyExists:
            If the user currency already exists in the database
        """
        model = User_Currency(database_connection, user_id, guild_id, None, currency)
        await model.save()
        return model

    @classmethod
    async def load(cls, database_connection:Connection, user_id:int, guild_id:int) -> "User_Currency":
        """Loads the user currency from the database.

        :param Connection database_connection: 
            Connection to the database used for fetching data
        
        :param int user_id:
            ID of the user who owns the currency
        
        :param int guild_id:
            ID of the guild the user owns the currency on
        
        :return: 
            An instance of User_Currency with the loaded data
        
        :raises NotFound:
            If the user currency is not found in the database
        """
        row = await database_connection.fetchrow(cls.LOAD, user_id, guild_id)
        if row is None:
            return NotFound("User_Currency", {"user_id": user_id, "guild_id": guild_id})
        return User_Currency(database_connection, row["user_id"], row["guild_id"], row["last_claimed"], row["balance"])
    
    async def save(self):
        if self._deleted:
            raise NoLongerExists("User_Currency", self.arguments(), self.data())

        try:
            await self._connection.execute(self.SAVE, self.__user_id, self.__guild_id, self.__last_claimed, self.__currency)
        except UniqueViolationError:
            raise AlreadyExists("User_Currency", self.arguments())

    async def delete(self):
        if self._deleted:
            raise NoLongerExists("User_Currency", self.arguments(), self.data())

        if await self._connection.fetchval(self.DELETE, self.__user_id, self.__guild_id) is None:
            raise NotFound("User_Currency", self.arguments())
        self._deleted = True

    def is_sufficient(self, amount:int) -> bool:
        """Checks if the user has enough currency to deduct the specified amount
        
        :param int amount:
            The amount to check for
        
        :returns bool:
            True if the user has enough currency, False otherwise
        """
        return self.__currency >= amount
    
    def credit(self, amount:int) -> int:
        """Credits the user with the specified amount
        
        :param int amount:
            The amount to credit
            
        :returns int:
            The new currency balance
        """
        self.__currency += amount
        return self.__currency

    def deduct(self, amount:int) -> int:
        """Deducts the specified amount from the user's currency
        
        :param int amount:
            The amount to deduct
        
        :returns int:
            The new currency balance
        
        :raises InsufficientBalance:
            If the user has insufficient balance
        """
        if not self.is_sufficient(amount):
            raise InsufficientBalance("User_Currency", self.__user_id, self.__guild_id, self.__currency, amount)
        self.__currency -= amount
        return self.__currency
    
    def ready_to_collect(self) -> bool:
        """Checks if the user is ready to collect his dailymoney
        
        :returns bool:
            True if the user is ready to collect his dailymoney, False otherwise"""
        if self.__last_claimed is None:
            return True
        current_date = datetime.now().date()
        last_claimed_date = self.__last_claimed.date()
        return current_date > last_claimed_date
    
    def arguments(self) -> dict[str, int]:
        return {"user_id": self.__user_id, "guild_id": self.__guild_id}
    
    def data(self) -> dict[str, int | datetime]:
        return {"last_claimed": self.__last_claimed, "currency": self.__currency}

    @property
    def user_id(self) -> int:
        """ID of the user who owns the currency"""
        return self.__user_id
    
    @property
    def guild_id(self) -> int:
        """ID of the guild"""
        return self.__guild_id
    
    @property
    def last_claimed(self) -> datetime | None:
        """Datetime the user has last claimed his dailymoney"""
        return self.__last_claimed
    
    @property
    def currency(self) -> int:
        """Current user balance"""
        return self.__currency
