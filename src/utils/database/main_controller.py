from utils.database.abc_adapter import DatabaseAdapter
from utils.database.abc_controller import DatabaseController
import asyncpg
from datetime import datetime, timedelta
from utils.calc_lvl_xp import calculate_current_level_experience

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
            
            today_timestamp = datetime.combine(current_time.date(), last_pickup.time())
            if current_time < today_timestamp:
                today_timestamp -= timedelta(days=1)
            return current_time.date() > today_timestamp.date()
        return True
    
    async def add_to_user_balance(self, guild_id:int, user_id:int, amount:int):
        """Adds to the balance of the specified user by the specified amount"""
        await self._adapter.execute_query("add_to_balance", (guild_id, user_id, amount))

    async def substract_from_user_balance(self, guild_id:int, user_id:int, amount:int):
        """Substracts from the balance of the specified user by the specified amount"""
        await self._adapter.execute_query("substract_from_balance", (amount, guild_id, user_id))
    
    async def reset_pickup_ready(self, user_id:int):
        """Resets the pickup cooldown to the current time"""
        await self._adapter.execute_query("reset_last_pickup", (user_id, ))

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

    async def create_dailymoney_settings_delete_message(self, main_message_id:int, message_id:int):
        """Insert row in `dailymoney_settings_delete` table to store information about the 'delete role' view"""
        await self._adapter.execute_query("add_dailymoney_delete_message", (main_message_id, message_id))

    async def update_dailymoney_settings_delete_role(self, message_id:int, role_id:int):
        """Update row in `dailymoney_settings_delete` table, to match the RoleSelectMenu interaction"""
        await self._adapter.execute_query("update_dailymoney_settings_delete_role", (role_id, message_id))

    async def get_dailymoney_settings_delete_row(self, message_id:int) -> int:
        """Returns the `role_id` and `main_message_id` for the matching row of the `dailymoney_settings_delete` table"""
        rows = await self._adapter.execute_query("get_dailymoney_settings_delete_row", (message_id, ))
        return (rows[0]["role_id"], rows[0]["main_message_id"])
    
    async def delete_dailymoney_roles_role(self, role_id:int):
        """Delete matching row in `dailymoney_roles` table to remove matching role from dailymoney roles"""
        await self._adapter.execute_query("delete_dailymoney_roles_role", (role_id, ))

    async def delete_dailymoney_settings_delete_row(self, message_id:int):
        """Removes the matching row from the 'dailymoney_settings_delete' table"""
        await self._adapter.execute_query("delete_dailymoney_settings_delete_row", (message_id, ))

    async def get_daily_salary(self, guild_id:int, user_roles_ids:tuple[int]) -> int | None:
        """Returns the daily salary determined by the role of the user with the highest priority"""
        rows = await self._adapter.execute_query("get_daily_salary", (guild_id, user_roles_ids))
        if rows:
            return rows[0]['daily_salary']
        return None
    
    async def create_pick_message(self, guild_id:int, channel_id:int, message_id:int, amount:int):
        """Creates a new entry in the `pick message` table, to link to the pick money message"""
        await self._adapter.execute_query("create_pick_message", (guild_id, channel_id, message_id, amount))

    async def delete_pick_message(self, message_id:int):
        await self._adapter.execute_query("delete_pick_message")

    async def get_last_pick_message(self, channel_id:int) -> tuple[int, int] | None:
        """Returns the message_id aswell as the value of the lastest pick_money message in the specified channel, deletes the row if existant"""
        row = await self._adapter.execute_query("get_latest_pick_money", (channel_id, ))
        if row:
            return (row[0]["message_id"], row[0]["amount"])
        return None
    
    async def add_to_user_experience(self, guild_id:int, user_id:int, experience:int) -> tuple[bool, int, int]:
        """Add to the user's experience on a specific guild. 
        
        The return value contains a bool, for when the user has leveled up, aswell as the current user level and experience"""
        # Get current stats of user
        row = await self._adapter.execute_query("get_level", (guild_id, user_id))
        if row:
            user_xp = row[0]["xp"]
            user_lvl = row[0]["level"]
        else:
            user_xp = 0
            user_lvl = 0

        # If the user has gained all the neccessary experience for the next level, level him up
        user_xp += experience
        level_up = False
        while user_xp >= (level_xp := calculate_current_level_experience(user_lvl)):
            user_xp -= level_xp
            user_lvl += 1
            level_up = True
        await self._adapter.execute_query("add_experience", (guild_id, user_id, user_xp, user_lvl, experience))
        return (level_up, user_lvl, user_xp)

    async def get_user_experience(self, guild_id:int, user_id:int) -> tuple[int, int] | None:
        """Returns the level and total experience of a user"""
        row = await self._adapter.execute_query("get_level", (guild_id, user_id))
        if row:
            return (row[0]["xp"], row[0]["total_xp"], row[0]["level"])
        return None
    
    async def get_user_rank(self, guild_id:int, user_id:int) -> int | None:
        row = await self._adapter.execute_query("get_leaderboard_position", (guild_id, user_id))
        if row:
            return row[0]["user_rank"]
        return None
    
    async def get_number_of_level_users(self, guild_id:int) -> int:
        """Returns the number of users who have xp on this guild"""
        row = await self._adapter.execute_query("get_level_users", (guild_id, ))
        return row[0]["count"]
    
    async def create_ranks_view(self, message_id:int, current_page:int):
        """Inserts a row to store informations about the interactable ranks message"""
        await self._adapter.execute_query("add_ranks_message", (message_id, current_page))

    async def get_ranks_page(self, message_id:int) -> int:
        """Returns the currently displayed page for a specific ranks view"""
        row = await self._adapter.execute_query("get_ranks_page", (message_id, ))
        return row[0]["current_page"]
    
    async def set_ranks_page(self, message_id:int, current_page:int):
        await self._adapter.execute_query("set_ranks_page", (current_page, message_id))
    
    async def get_ranks_page_users(self, guild_id:int, page_number:int, user_per_page:int = 20) -> list[tuple]:
        """Returns users for the current ranks page"""
        rows = await self._adapter.execute_query("get_ranks_page_users", (guild_id, user_per_page, page_number * user_per_page))
        users_info = []
        for row in rows:
            users_info.append((row["user_id"], row["level"], row["xp"], row["total_xp"]))
        return users_info
    
    async def get_channel_functionality(self, channel_id:int) -> tuple[bool]:
        """Returns the enabled functionality for a specific channel
        
        - [0]: Experience enabled? Default: No"""
        row = await self._adapter.execute_query("get_channel_functionality", (channel_id, ))
        if row:
            return (row[0]["experience"], row[0]["pick_money"])
        return None
    
    async def get_experience_settings(self, channel_id:int) -> tuple[float] | None:
        row = await self._adapter.execute_query("get_experience_settings", (channel_id, ))
        if row:
            return (row[0]["default_multiplier"], row[0]["minimum_threshold"], row[0]["maximum_experience"])
        return None

    async def user_for_experience_applicable(self, guild_id:int, user_id:int, minimum_time_delta:float = 60.0) -> bool:
        """Check whater or not the user is applicable to recieve experience"""
        row = await self._adapter.execute_query("get_last_xp_pickup", (user_id, guild_id))
        if row:
            last_pickup:datetime = row[0]["last_xp_pickup"]
            if last_pickup == None or datetime.now().timestamp() - last_pickup.timestamp() >= minimum_time_delta:
                return True
            return False
        return True
    
    async def reset_user_experience_gain(self, guild_id:int, user_id:int,):
        """Resets the last_xp_pickup timer to the current time"""
        await self._adapter.execute_query("reset_user_xp_gain_timer", (guild_id, user_id))
        
    async def get_pick_money_settings(self, channel_id:int) -> tuple[int]:
        """Returns pick money settings of the specified channel"""
        row = await self._adapter.execute_query("get_pick_money_settings", (channel_id, ))
        if row:
            return (row[0]["min_amount"], row[0]["max_amount"], row[0]["probability"])
        return None
    
    async def create_experience_settings_message(self, channel_id:int, original_message_id:int, message_id:int, default_multiplier:float, minimum_threshold:int, maximum_experience:int):
        """Creates a row in the "channel_experience_settings" table to store the data about the configuration message"""
        await self._adapter.execute_query("create_experience_settings_message", (channel_id, message_id, original_message_id, default_multiplier, minimum_threshold, maximum_experience))

    async def get_experience_settings_message(self, channel_id:int) -> tuple[float, int, int]:
        """Returns the data for the matching configuration message"""
        row = await self._adapter.execute_query("get_experience_settings_message", (channel_id, ))
        if row:
            return (row[0]["default_multiplier"], row[0]["minimum_threshold"], row[0]["maximum_experience"], row[0]["message_id"], row[0]["original_message_id"])
        return None
