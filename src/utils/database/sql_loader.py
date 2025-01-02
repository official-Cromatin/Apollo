from enum import Enum
from pathlib import Path
import logging
import aiofiles
from datetime import datetime
from utils.datetime_tools import get_elapsed_time_milliseconds

class Database_Types(Enum):
    POSTGRESQL = "postgresql"

class PathNotFound(Exception):
    pass

class IllegalFileFound(Exception):
    pass

class SQL_Loader:
    """Serves as an abstraction layer between the SQL scripts contained in the files and the runtime environment.

    Loaded files are saved in the cache, which can be emptied on command and is then repopulated"""
    def __init__(self, database_type:Database_Types, base_path:Path):
        """Creates a new instance, also checks whether the path is valid

        Note: At the beginning the cache is empty"""
        self.__cache:dict[str, str] = {}
        self.__base_path:Path = base_path
        self.__database_type = database_type
        self.__logger = logging.getLogger("utils.sqlloader")

        # Check if the path is valid
        if not self.__base_path.exists():
            raise PathNotFound(f"The specified path ({base_path}) does not exist")
        self.__database_path = base_path / database_type.value
    
    @property
    def database_type(self) -> Database_Types:
        """The type of database for which the files were (and are) loaded"""
        return self.__database_type
    
    @property
    def base_path(self) -> Path:
        """The `base_path` specified during instantiation"""
        return self.__base_path
    
    @property
    def cache_size(self) -> int:
        """The size of the cache (number of elements)"""
        return len(self.__cache)

    async def __load_file(self, file_path:Path):
        """Auxiliary method to load a single file into the cache"""
        async with aiofiles.open(file_path, mode = "r") as file:
            content = await file.read()

        file_name = str(file_path.relative_to(self.__database_path))
        file_name = file_name.replace("\\", ".").replace(".sql", "")
        self.__cache[file_name] = content

        self.__logger.debug(f"{file_name} loaded into cache")

    async def load_all(self, ignore:bool = False):
        """Loads every single .sql file (start path: `{base_path}/{database_type}/*`) into the cache

        If a non .sql file is found, an error is triggered (`ignore = false`, prevents an exception from being raised)"""
        begin = datetime.now().timestamp()
        # Get all files in the database directory
        files:list[Path] = []
        for file_path in self.__database_path.rglob("*"):
            if not file_path.is_file():
                continue

            if file_path.suffix != ".sql":
                if not ignore:
                    raise IllegalFileFound(f"Non-SQL file {file_path.name} was found in directory")
                self.__logger.warning(f"Non-SQL file {file_path.name} was found in directory")
                continue
            
            files.append(file_path)
        self.__logger.debug(f"All {len(files)} files in directory {self.__database_path} will be loaded into cache")

        # Load each file into the cache
        for file_path in files:
            await self.__load_file(file_path)
        self.__logger.info(f"All {len(files)} files in directory {self.__database_path} loaded into cache after {get_elapsed_time_milliseconds(datetime.now().timestamp() - begin)}")
    
    async def get_file(self, name:str) -> str:
        """Returns the file searched for; if the file is not in the cache, it is searched for. 
        
        If it cannot be found, an error is raised.
        
        The required path needs to be specified in dot notation (“dml.customer.cart” -> “{base_path}/{database_type}/dml/customer/cart.sql”)"""
        
        # Fix the file name
        if "/" in name:
            self.__logger.warning(f"The file name ({name}) must be specified in dot notation. All slashes have been replaced by dots")
            name = name.replace("/", ".")
        
        # Return the content of the file if in cache
        if name in self.__cache:
            self.__logger.debug(f"Resource {name} served from cache")
            return self.__cache[name]
        
        # Try to load the missing file into cache
        file_name = name.replace(".", "/") + ".sql"
        file_path = self.__database_path / file_name
        await self.__load_file(file_path)
        self.__logger.info(f"File {name} subsequently loaded into cache")
        return self.__cache[name]

    def remove_file(self, name:str, ignore:bool = False):
        """Removes the file with the specified name from the cache

        If the file is not yet in the cache, an error is triggered (`ignore = false`, prevents an exception from being raised)"""
        try:
            del self.__cache[name]
        except ValueError as error:
            if ignore:
                self.__logger.error(f"{name} does not exist in the cache and could not be removed")
                return
            raise error

    def clear_cache(self):
        """Clears the cache; when a resource is requested again, it must be reloaded from the file system"""
        self.__cache.clear()

    async def reload_cache(self, ignore:bool = False):
        """Reloads all files already loaded again into the cache
        
        If a file is no longer available, an error is generated (`ignore = true`, prevents an exception from being raised)"""
        begin = datetime.now().timestamp()
        # Get the path for each file
        loaded_files:list[Path] = []
        for loaded_file in self.__cache.keys():
            file_name = loaded_file.replace(".", "/") + ".sql"
            file_path = self.__database_path / file_name
            loaded_files.append(file_path)

        # Clear the cache and reload all files
        self.__cache.clear()
        for file_path in loaded_files:
            await self.__load_file(file_path)
        self.__logger.info(f"{len(loaded_files)} files have been reloaded after {get_elapsed_time_milliseconds(datetime.now().timestamp() - begin)}")
