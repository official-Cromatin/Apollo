from database.models.base_model import Base_Model
from database.models.exceptions import NotFound, NoLongerExists, AlreadyExists
from asyncpg import Connection, UniqueViolationError
from datetime import datetime
import math


class User_Experience(Base_Model):
    """
    Represents the experience of a user.
    
    Offers functions to manipulate the amount of experience (add, withdraw) and to calculate the required experience points for the current and target level
    
    The data can be accessed via the displayed properties
    
    | Attribute name    | Mutability   | Description                                            |
    |-------------------|--------------|--------------------------------------------------------|
    | `user_id`         | `read-only`  | ID of the user who owns the experience                 |
    | `guild_id`        | `read-only`  | ID of the guild the user owns the experience on        |
    | `experience`      | `read-only`  | Collected experience points on the current level       |
    | `total_experience`| `read-only`  | Total experience points gained                         |
    | `level`           | `read-only`  | Current user level                                     |
    | `last_xp_reward`  | `read-only`  | Datetime the user has last received experience points  |
    """
    LOAD = ""
    SAVE = ""
    DELETE = ""

    def __init__(self, database_connection:Connection, user_id:int, guild_id:int, experience:int, total_experience:int, level:int, last_xp_reward:datetime | None):
        super().__init__(database_connection)
        self.__user_id = user_id
        self.__guild_id = guild_id
        self.__experience = experience
        self.__total_experience = total_experience
        self.__level = level
        self.__last_xp_reward = last_xp_reward

    def __str__(self):
        return f"User_Experience({self.arguments()}, {self.data()})"

    @classmethod
    async def create(cls, database_connection:Connection, user_id:int, guild_id:int, experience:int = 0, total_experience:int = 0, level:int = 0, last_xp_reward:datetime = None) -> "User_Experience":
        """Creates a new model with the specified data.
        
        :param Connection database_connection:
            Connection to the database used for later actions
            
        :param int user_id:
            ID of the user who owns the experience
        
        :param int guild_id:
            ID of the guild the user owns the experience on
        
        :param int experience:
            Collected experience points on the current level
        
        :param int total_experience:
            Total experience points gained
        
        :param int level:
            Current user level
        
        :param datetime last_xp_reward:
            Datetime the user has last received experience points
            
        :return:
            An instance of User_Experience with the specified data
            
        :raises AlreadyExists:
            If the user experience already exists in the database
        """
        model = User_Experience(database_connection, user_id, guild_id, experience, total_experience, level, last_xp_reward)
        await model.save()
        return model
    
    @classmethod
    async def load(cls, database_connection:Connection, user_id:int, guild_id:int) -> "User_Experience":
        """Loads the user experience from the database.

        :param Connection database_connection: 
            Connection to the database used for fetching data
        
        :param int user_id:
            ID of the user who owns the experience
        
        :param int guild_id:
            ID of the guild the user owns the experience on
        
        :return: 
            An instance of User_Experience with the loaded data
        
        :raises NotFound:
            If the user experience is not found in the database
        """
        row = await database_connection.fetchrow(cls.LOAD, user_id, guild_id)
        if row is None:
            return NotFound("User_Experience", {"user_id": user_id, "guild_id": guild_id})
        return User_Experience(database_connection, row["user_id"], row["guild_id"], row["experience"], row["total_experience"], row["level"], row["last_xp_reward"])

    async def save(self) -> "User_Experience":
        if self._deleted:
            raise NoLongerExists("User_Experience", self.arguments(), self.data())
        
        try:
            await self._connection.execute(self.SAVE, self.__user_id, self.__guild_id, self.__experience, self.__total_experience, self.__level, self.__last_xp_reward)
        except UniqueViolationError:
            raise AlreadyExists("User_Experience", self.arguments())
        return self
        
    async def delete(self) -> "User_Experience":
        if self._deleted:
            raise NoLongerExists("User_Experience", self.arguments(), self.data())
        
        if await self._connection.fetchval(self.DELETE, self.__user_id, self.__guild_id) is None:
            raise NotFound("User_Experience", self.arguments())
        self._deleted = True
        return self
    
    @staticmethod
    def calculate_current_level_experience(current_level:int) -> int:
        """Calculates the amount of experience required to complete this level
        
        :param int current_level:
            The current level of the user
            
        :return:
            The amount of experience points required to complete the current level
        """
        return int(5 * math.pow(current_level, 2) + 50 * current_level + 100)
    
    @staticmethod
    def calculate_total_level_experience(target_level:int) -> int:
        """Calculates the total XP required to reach (not complete) a certain level
        
        :param int target_level:
            The target level to reach
        
        :return:
            The total amount of experience points required to reach the target level
        """
        if target_level <= 0:
            return 0
        return int((5 / 3) * math.pow(target_level, 3) + 
                (45 / 2) * math.pow(target_level, 2) + 
                (455 / 6) * target_level)

    def add_experience(self, amount: int) -> tuple[bool, int, int]:
        """Adds the specified amount of experience to the user
        
        :param int amount: 
            The amount of experience to add
        
        :rtype: tuple[bool, int, int]
        :returns: 
            - **bool** – True if the user has leveled up, False otherwise

            - **int** – The new user level

            - **int** – The new total experience points
        """
        if amount < 0:
            raise ValueError("The amount to be added must be positive")

        self.__experience += amount
        level_up = False

        # Level the user up as long as his experience on the current level is greater than the required experience
        while self.__experience >= (level_xp := self.calculate_current_level_experience(self.__level)):
            self.__experience -= level_xp
            self.__level += 1
            level_up = True

        self.__total_experience += amount
        return (level_up, self.__level, self.__experience)
    
    def withdraw_experience(self, amount:int) -> tuple[bool, int, int]:
        """Withdraws the specified amount of experience from the user
        
        :param int amount:
            The amount of experience to withdraw
        
        :rtype: tuple[bool, int, int]
        :returns:
            - **bool** – True if the user has leveled down, False otherwise

            - **int** – The new user level

            - **int** – The new total experience points
        """
        if amount < 0:
            raise ValueError("The amount to be withdrawn must be positive")

        new_total_experience = self.__total_experience - amount
        if new_total_experience < 0:
            raise ValueError("The user cannot have negative experience points")

        # Calculate the new level and experience points
        old_level = self.__level
        self.__experience = 0
        self.__level = 0
        self.__total_experience = 0
        self.add_experience(new_total_experience)

        return (old_level > self.__level, self.__level, self.__experience)
    
    def arguments(self) -> dict[str, int]:
        return {"user_id": self.__user_id, "guild_id": self.__guild_id}
    
    def data(self) -> dict[str, int | datetime]:
        return {"experience": self.__experience, "total_experience": self.__total_experience, "level": self.__level, "last_xp_reward": self.__last_xp_reward}
    
    @property
    def user_id(self) -> int:
        """ID of the user who owns the experience"""
        return self.__user_id
    
    @property
    def guild_id(self) -> int:
        """ID of the guild"""
        return self.__guild_id
    
    @property
    def experience(self) -> int:
        """Collected experience points on the current level"""
        return self.__experience
    
    @property 
    def total_experience(self) -> int:
        """Total experience points gained"""
        return self.__total_experience
    
    @property
    def level(self) -> int:
        """Current user level"""
        return self.__level
    
    @property
    def last_xp_reward(self) -> datetime | None:
        """Datetime the user has last received experience points"""
        return self.__last_xp_reward
