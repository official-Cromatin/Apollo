from utils.database.abc_adapter import DatabaseAdapter
from utils.database.abc_controller import DatabaseController

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