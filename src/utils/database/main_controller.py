from utils.database.abc_adapter import DatabaseAdapter
from utils.database.abc_controller import DatabaseController

class Main_DB_Controller(DatabaseController):
    """Controller used by most """
    def __init__(self, database_adapter: DatabaseAdapter) -> None:
        super().__init__(database_adapter)

