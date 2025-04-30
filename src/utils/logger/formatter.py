from logging import Formatter, LogRecord
from colorama import Style, Fore

class Colored_Formatter(Formatter):
    def __init__(self, fmt=None, datefmt='%Y-%m-%d %H:%M:%S', style='%'):
        super().__init__(fmt, datefmt, style)
        
    def format(self, record:LogRecord):
        # Format the date bold
        date = f"{Style.BRIGHT}{Fore.BLACK}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}"
        
        # Set the colors for the levelname and colorize it
        levelname_color = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.BLUE,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': f"{Style.BRIGHT}{Fore.RED}"
        }
        levelname = f"{levelname_color.get(record.levelname, Fore.WHITE)}{record.levelname:<8}{Fore.RESET}{Style.RESET_ALL}"
        
        # Construct the name with optional additions from extra
        record_name = record.name
        if hasattr(record, "iname"):
            record_name += f".{record.iname}"
        if hasattr(record, "id"):
            record_name += f".{record.id}"
        name = f"{Fore.MAGENTA}{record_name:<20}{Fore.RESET}"
        
        # Leave the message as it is
        message = record.getMessage()
        
        # Combine all and return
        formatted_record = f"{date} {levelname} {name} {message}"
        return formatted_record