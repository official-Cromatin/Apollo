from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
import logging
from utils.datetime_tools import get_elapsed_time_milliseconds
from os import listdir

class DatabaseAdapter(ABC):
    """Abstract class to ease the addition and integration of new database systems.
    
    To implement a new database system, you'll need to override all the abstract methods of the class"""
    # Constants to change where files to create missing tables and querys are found
    SQL_TOP_FOLDER_NAME = "database"
    DATA_DEFINITION_FILE_PREFIX = "ddl-"
    QUERY_FILE_PREFIX = "query-"

    VERSION = "2.2"
    number_of_instances = 0

    def __init__(self, database_type:str, top_path:str):
        """Constructor to set the needed values"""
        self._type = database_type
        self._top_path = top_path
        self._database_folder = Path(top_path) / self.__class__.SQL_TOP_FOLDER_NAME / database_type
        self._instance_number = self.__class__.number_of_instances
        self.__class__.number_of_instances += 1
        self._logger = logging.getLogger(f"utils.dba.{self._type}.{self._instance_number}")
        self._logger.debug(f"New instance {self._instance_number} of class created (Type of adapter: {self._type}) (Folder: {self._database_folder})")

        # Load all the files from the disk
        begin_load = datetime.now().timestamp()
        self._logger.debug("Loading query executables ...")
        db_files = self.load_all_files()
        no_of_querys = len(db_files["query"])
        no_of_tables = len(db_files["table"])
        self._logger.info(f"Loaded {no_of_querys} query and {no_of_tables} table define executable, after {get_elapsed_time_milliseconds(datetime.now().timestamp() - begin_load)}")

        # Save the known querys
        self._querys = db_files["query"]
        self._ddls = db_files["table"]

    def get_type(self) -> str:
        return self._type
    
    def get_folder(self) -> str:
        return self._database_folder

    @abstractmethod
    async def execute_query(self, query_key: str, arguments: tuple = ()) -> list:
        """Method to execute a normal query, returns a tuple with the retrieved values"""
        pass

    # @abstractmethod
    # async def execute_dict_query(self, query_key:str, arguments: tuple = ()) -> dict:
    #     """Method to execute a query in dictionary mode, returns a tuple with the retrieved data assigned to a key (same as column name)"""
    #     pass

    # @abstractmethod
    # def insert_many(self, query_key:str, arguments: list) -> None:
    #     """Method to insert many values into the database, the argument list contains tuples with the values that should be inserted"""
    #     pass

    # @abstractmethod
    # def commit_changes(self):
    #     """Method to commit the made changes to the database"""
    #     pass

    # @abstractmethod
    # def rollback_changes(self):
    #     """Method to rollback to the previous state"""
    #     pass
    
    # @abstractmethod
    # def return_number_of_defined_querys(self) -> int:
    #     """Returns the number of defined querys"""
    #     pass

    @abstractmethod
    def _check_table(self, table_name: str, create_statement: str):
        """Internal abstract method to check if the given table does exist. If it doesnt, the `create_statement` is executed to create it"""
        pass

    @abstractmethod
    def close_connection(self):
        """Method to close the connection to the database properly"""
        pass

    # @abstractmethod
    # def start_routine(self):
    #     """Method that is ran before the database connection is opened"""
    
    # @abstractmethod
    # def stop_routine(self):
    #     """Method that is ran before the database connection is closed"""

    def _open_when_starting_with(self, file_name:str, file_prefix:str, remove_breaklines:bool = True, remove_comments:bool = True):
        """Helpermethod to check if the specified file starts with the given prefix, load it if it does so.
        
        Returns the name with the prefix of the filename removed aswell as the content of the file. Nothing is returned if the file does not start with the prefix"""
        # Check if the file starts with the prefix
        if file_name.startswith(file_prefix):
            # Cut away the beginning of the file name
            query_name = file_name[len(file_prefix):].replace(".sql", "")
            file_path = Path(self._database_folder) / file_name

            # Open the file and load its content
            with open(file_path, "r") as file:
                content = file.read()

                # Remove comments defines in the file
                if remove_comments:
                    # Spilt the content after breaklines
                    split_content = content.split("""\n""")
                    new_content = ""

                    # Iterate over the lines to test
                    for line in split_content:
                        # Test if the line is a comment
                        if line.startswith("--"):
                            pass

                        # Test if the line is empty
                        elif line == "":
                            pass

                        else:
                            new_content += line + "\n"

                    content = new_content

                # Remove used breaklines from the query
                if remove_breaklines:
                    content = content.replace("""\n""", " ")
        
            # Return the values as tuple
            return query_name, content
        
    async def check_tables(self, table_names:list[str] = None):
        """Abstract helpermethod to check if all the neccesary tables exist, if not, they will be created"""
        if not table_names:
            table_names = self._ddls.keys()

        self._logger.debug("Checking the existence of all specified tables ...")
        begin_check = datetime.now().timestamp()
        for table_name in table_names:
            await self._check_table(table_name, self._ddls[table_name])
        self._logger.info(f"Checked the existence of all specified tables after {get_elapsed_time_milliseconds(datetime.now().timestamp() - begin_check)}")

    def list_files(self) -> list[str]:
        """Method to list all files in the folder of the database system"""
        file_names = []
        # Test if the folder exists
        if Path.exists(self._database_folder):
            # Iterate over the content
            for file_name in listdir(self._database_folder):
                file_path = Path(self._database_folder) / file_name
                # Check if it is an file
                if Path.is_file(file_path):
                    file_names.append(file_name)

        return file_names

    def load_sql_file(self, file_name:str) -> str:
        """Method to load a specific sql file and return the content of the file. Errors are not catched!"""
        file_path = Path(self._database_folder) / file_name
        # Test if the path exists
        if Path.exists(file_name):
            # Open the file and return the content
            with open(file_path, "r") as file:
                content = file.read()
            return content
        else:
            # Raise error when the file is not found
            raise FileNotFoundError
        
    def load_all_query_files(self) -> dict:
        """Method to load all the query files of the specified database system. 
        
        The content of the files is returned in an dictionary indexed by the name of the files with the filename (file prefix excluded) being the key"""
        files = self.list_files()
        querys = {}

        # Iterate over the filename of all files
        for file_name in files:
            returned = self._open_when_starting_with(file_name, DatabaseAdapter.QUERY_FILE_PREFIX)

            # Check if the returned value is not null
            if returned:
                querys[returned[0]] = returned[1]

        return querys
    
    def load_all_table_files(self) -> dict:
        """Method to load all the ddl files to create missing tables.
        
        The content of the files is returned in an dictionary indexed by the name of the files with the filename (file prefix excluded) being the key"""
        files = self.list_files()
        definitions = {}

        # Iterate over the filename of all files
        for file_name in files:
            returned = self._open_when_starting_with(file_name, DatabaseAdapter.DATA_DEFINITION_FILE_PREFIX)

            # Check if the returned value is not null
            if returned:
                definitions[returned[0]] = returned[1]

        return definitions
    
    def load_all_files(self, debug_mode_enabled:bool = True) -> dict:
        """Method to load all files for the database including those to create tables and execute querys.
        
        The dictionary has two top level keys `table` and `query`, containing another dictionary with the filename (file prefix removes) being the key and the value the file content"""
        files = self.list_files()
        db_files = {
            "table": {},
            "query": {}
        }

        if debug_mode_enabled:
            optimize = False
        else:
            optimize = True
        
        # Iterate over the filename of all files
        for file_name in files:
            returned = self._open_when_starting_with(file_name, DatabaseAdapter.QUERY_FILE_PREFIX, optimize, optimize)
            #print("query", returned)

            # Check if the returned value is not null
            if returned:
                db_files["query"][returned[0]] = returned[1]
            else:
                # Try the other prefix if the first one does not match
                returned = self._open_when_starting_with(file_name, DatabaseAdapter.DATA_DEFINITION_FILE_PREFIX, optimize, optimize)
                #print("table", returned)

                if returned:
                    db_files["table"][returned[0]] = returned[1]
                
                else:
                    print("Ingored", file_name, "since no prefix matches")

        return db_files