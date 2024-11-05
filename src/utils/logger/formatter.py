from logging import Formatter
from colorama import Style, Fore

class Colored_Formatter(Formatter):
    def __init__(self, fmt=None, datefmt='%Y-%m-%d %H:%M:%S', style='%'):
        super().__init__(fmt, datefmt, style)
        
    def format(self, record):
        # Formatieren des Zeitstempels fett
        date = f"{Style.BRIGHT}{Fore.BLACK}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}"
        
        # Färben des Log-Levels mit fester Breite
        levelname_color = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.BLUE,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': f"{Style.BRIGHT}{Fore.RED}"
        }
        levelname = f"{levelname_color.get(record.levelname, Fore.WHITE)}{record.levelname:<8}{Fore.RESET}{Style.RESET_ALL}"
        
        # Färben des Logger-Namens in Magenta mit fester Breite
        name = f"{Fore.MAGENTA}{record.name:<20}{Fore.RESET}"
        
        # Die Nachricht bleibt unverändert
        message = record.getMessage()
        
        # Zusammenfügen der gefärbten Teile
        formatted_record = f"{date} {levelname} {name} {message}"
        return formatted_record