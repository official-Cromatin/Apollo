from utils.database.abc_adapter import DatabaseAdapter
from utils.database.abc_controller import DatabaseController
import asyncpg
from datetime import datetime

class Main_DB_Controller(DatabaseController):
    """Controller used by most """
    def __init__(self, database_adapter: DatabaseAdapter) -> None:
        super().__init__(database_adapter)

    async def get_user_currency(self, guild_id:int, user_id:int) -> int | None:
        """Queries and returns the account balance of a user, if it does not exist, the query returns None"""
        return_value = await self._adapter.execute_query("get_currency", (guild_id, user_id))
        if return_value:
            return return_value[0]["balance"]
        return None
    
    async def get_number_of_users(self, guild_id:int) -> int:
        """Querys and returns the number of users who ever owned money on an certain guild"""
        return_value = await self._adapter.execute_query("currency_guild_users", (guild_id, ))
        return return_value[0]["count"]
    
    async def get_leaderboard_page_users(self, guild_id:int, offset:int, limit:int = 9) -> list[asyncpg.Record]:
        """Querys and returns the currency for an specified amount of users, on an specified guild with an specified offset"""
        return await self._adapter.execute_query("leaderboard_users", (guild_id, limit, offset))
    
    async def create_leaderboard_page(self, message_id:int, current_page:int):
        """Creates a row in the database"""
        await self._adapter.execute_query("create_leaderboard_view", (message_id, current_page))

    async def get_leaderboard_page(self, message_id:int) -> int:
        """Querys and returns the current page for a leaderboard view"""
        return_value = await self._adapter.execute_query("get_leaderboard_page", (message_id, ))
        return return_value[0]["current_page"]
    
    async def update_leaderboard_page(self, message_id:int, current_page:int):
        """Updates the value in the database, to match the currently displayed page of the message"""
        await self._adapter.execute_query("update_leaderboard_page", (current_page, message_id))

    async def dailymoney_pickup_ready(self, user_id:int) -> bool:
        """Querys and compares the last time the specified user has collected his dailymoney
        
        Returns true if the pickup is ready and false if less than 24h have passed"""
        return_value = await self._adapter.execute_query("get_last_pickup", (user_id, ))
        if return_value:
            last_pickup: datetime | None = return_value[0]["last_pickup"]
            current_time = datetime.now()
            if (current_time - last_pickup).total_seconds() > 86400:
                return True
            else:
                return False
        await self.initialize_pickup_ready(user_id)
        return True
    
    async def add_to_user_balance(self, user_id:int, amount:int):
        """Increments the balance of the specified user by the specified amount"""
        await self._adapter.execute_query("add_to_balance", (amount, user_id))
    
    async def reset_pickup_ready(self, user_id:int):
        """Resets the pickup cooldown to the current time"""
        await self._adapter.execute_query("reset_last_pickup", (user_id, ))

    async def initialize_pickup_ready(self, user_id:int):
        """Inserts the row into the table, the first time a user accesses the data"""
        await self._adapter.execute_query("init_last_pickup", (user_id, ))

    async def get_dailymoney_roles(self, guild_id:int) -> list[tuple]:
        """Querys and returns dailymoney roles for a certain guild"""
        rows = await self._adapter.execute_query("get_dailymoney_roles", (guild_id, ))
        roles_data = []
        for role_data in rows:
            roles_data.append((
                role_data["role_priority"],
                role_data["role_id"],
                role_data["daily_salary"]
            ))
        return roles_data
    
    
    async def create_role_message(self, main_message_id:int, message_id:int, edit_mode:int):
        """Creates a row in the "dailymoney_role_settings" table to store informations about the message"""
        await self._adapter.execute_query("add_role_message", (main_message_id, message_id, edit_mode))

    async def get_role_message_data(self, message_id:int):
        """Returns the data for a certain """
        rows = await self._adapter.execute_query("get_role_message_data", (message_id, ))
        row = rows[0]
        return (row["role_id"], row["priority"], row["daily_salary"], row["main_message_id"], row["edit_mode"])
    
    async def set_role_for_role_message(self, message_id:int, role_id:int):
        """Updates the role_id field in the row matching the message id"""
        await self._adapter.execute_query("set_dailymoney_settings_role", (role_id, message_id))

    async def set_priority_for_role_message(self, message_id:int, priority:int):
        """Updates the priority field in the row matching the message id"""
        await self._adapter.execute_query("set_datilymoney_settings_priority", (priority, message_id))

    async def set_salary_for_role_message(self, message_id:int, daily_salary:int):
        """Updates the daily salary field in the row matching the message id"""
        await self._adapter.execute_query("set_dailymoney_settings_salary", (daily_salary, message_id))

    async def add_dailymoney_role(self, guild_id:int, role_priority:int, role_id:int, daily_salary:int):
        """Adds a row to the dailymoney_roles table, to respect the addition of the dailymoney role"""
        await self._adapter.execute_query("add_dailymoney_role", (guild_id, role_priority, role_id, daily_salary))

    async def remove_dailymoney_add_role_message(self, message_id:int):
        """Deletes the specified row of the dailymoney_settings table"""
        await self._adapter.execute_query("remove_dailymoney_settings", (message_id, ))

    async def get_dailymoney_edit_mode(self, message_id:int) -> int:
        """Returns the edit mode for the specified message"""
        rows = await self._adapter.execute_query("get_dailymoney_edit_mode", (message_id, ))
        return rows[0]["edit_mode"]
    
    async def get_role_ids_for_guild(self, guild_id:int) -> list[int]:
        """Returns a list of all role_ids presend on a certain guild and specified for dailymoney influencing roles"""
        rows = await self._adapter.execute_query("get_guild_dailymoney_roles", (guild_id, ))
        role_ids = []
        for row in rows:
            role_ids.append(row["role_id"])
        return role_ids
    
    async def update_settings_from_role(self, role_id:int, message_id:int):
        """Updates the row containing the settings for the edit role view"""
        await self._adapter.execute_query("update_settings_from_role", (role_id, message_id))

    async def update_dailymoney_role(self, role_id:int, role_priority:int, daily_salary:int):
        """Updates the values for the specified dailymoney role"""
        await self._adapter.execute_query("update_dailymoney_role", (role_priority, daily_salary, role_id))