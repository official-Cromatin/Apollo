from utils.database.abc_adapter import DatabaseAdapter
import asyncpg
from datetime import datetime
from utils.datetime_tools import get_elapsed_time_milliseconds

class PostgreSQL_Adapter(DatabaseAdapter):
    """Adapter used to connect to an PostgreSQL type database"""
    def __init__(self, username:str, password:str, database_name:str, adress:str, top_path: str, port:int, min_pool_size:int, max_pool_size:int):
        super().__init__("psql", top_path)
        self.__username = username
        self.__password = password
        self.__database_name = database_name
        self.__adress = adress
        self.__port = port
        self.__min_pool_size = min_pool_size
        self.__max_pool_size = max_pool_size

    @classmethod
    async def create_adapter(cls, username:str, password:str, database_name:str, adress:str, top_path: str, port:int = 5432, min_pool_size:int = 5, max_pool_size:int = 10):
        self = cls(username, password, database_name, adress, top_path, port, min_pool_size, max_pool_size)
        await self.connect()
        return self

    async def connect(self):
        self._logger.debug(f"Connecting to database ({self.__username}@{self.__adress}:{self.__port}/{self.__database_name}) ...")
        connection_begin = datetime.now().timestamp()
        try:
            self.__connection_pool = await asyncpg.create_pool(
                user = self.__username,
                password = self.__password,
                database = self.__database_name,
                port = self.__port,
                host = self.__adress,
                min_size = self.__min_pool_size,
                max_size = self.__max_pool_size,
            )
        except asyncpg.exceptions.InvalidPasswordError as error:
            self._logger.critical("Establishment of the connection to the database failed, due to an invalid password")
            raise error
        else:
            self._logger.info(f"Connection to database successfully established after {get_elapsed_time_milliseconds(datetime.now().timestamp() - connection_begin)}")

    async def execute_query(self, query_key: str, arguments: tuple = ()) -> list[asyncpg.Record]:
        """Method to execute a normal query, returns a tuple with the retrieved values"""
        connection: asyncpg.Connection
        async with self.__connection_pool.acquire() as connection:
            records = await connection.fetch(self._querys[query_key], *arguments)
        return records

    async def _check_table(self, table_name: str, create_statement: str):
        """Internal method to check if the given table does exist. If it doesnt, the `create_statement` is executed to create it"""
        connection: asyncpg.Connection
        async with self.__connection_pool.acquire() as connection:
            table_exists = await connection.fetchval(f"""
                SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' AND tablename = $1
                );
            """, table_name)

            if table_exists:
                self._logger.debug(f"Table {table_name} already exists")
            else:
                await connection.execute(create_statement)
                self._logger.info(f"Table {table_name} was missing, and has been created")

    async def close_connection(self):
        await self.__connection_pool.close()
        self._logger.info("Connection to database has been closed")