from utils.database.abc_adapter import DatabaseAdapter
from utils.database.abc_controller import DatabaseController
import asyncpg

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