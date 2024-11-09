from abc import ABC
from utils.database.abc_adapter import DatabaseAdapter
import logging

class DatabaseController(ABC):
    """Controllerclass to make use of the adapters"""
    VERSION = "2.2"
    number_of_instances = 0

    def __init__(self, database_adapter: DatabaseAdapter) -> None:
        """Creates a new adapter object, capeable of executing querys"""
        self._instance_number = self.__class__.number_of_instances
        self.__class__.number_of_instances += 1

        self._logger = logging.getLogger(f"utils.dbc.{self._instance_number}")
        self._logger.debug(f"New instance {self._instance_number} of class created (Type of adapter: {database_adapter.get_type()}) (Folder: {database_adapter.get_folder()})")

        self._adapter = database_adapter

    def shutdown(self):
        """Shuts the connected adapter down"""
        self._adapter.close_connection()

    