import configparser
import logging
from os.path import isfile, split
from pathlib import Path
from shutil import copy

class Advanced_ConfigParser(configparser.ConfigParser):
    """Utility class to ease the use of the configparser libary"""
    VERSION = "2.5"
    number_of_instances = 0

    def __init__(self, path:str, allow_template:bool = True, allow_update:bool = True) -> None:
        """
        Initializes the Advanced_ConfigParser instance.

        Args:
            path (str): The path to the configuration file.
            allow_template (bool, optional): Determines if an existing template can be used when the config file is missing. Default is True.
            allow_update (bool, optional): Specifies if the config file should be updated based on a template. Default is True.

        This constructor loads the configuration file if it exists, optionally creates one from a template if allowed,
        and can update the configuration based on the template. It also initializes logging and tracks pending changes.
        """
        super().__init__()
        self.__instance_number = self.__class__.number_of_instances
        self.__class__.number_of_instances += 1
        self.__from_template = False

        self.__logger = logging.getLogger(f"utils.config.{self.__instance_number}")
        self.__logger.debug(f"New instance {self.__instance_number} of class created")

        # Check existence of provided file
        self.__template_path = self.__get_template_path(path)
        if isfile(path):
            self.__logger.debug(f"Opening existing file at path: '{path}'")
        else:
            # Check if it is allowed to use an existing template
            if allow_template:
                if isfile(self.__template_path):
                    self.__logger.info(f"Using existing template file {self.__template_path}")
                    copy(self.__template_path, path)
                    self.__from_template = True
                else:
                    self.__logger.warning("No potential template found, starting with empty file")
        
        # Load the configfile
        self.__file_path = path
        self.__pending_changes = 0

        try:
            self.read_file(open(path))
        except:
            pass
        else:
            self.__logger.info(f"Successfully opened config file at path {path}")

        # Check for update if allowed
        if allow_update:
            self.check_for_update()
    
    def __get_template_path(self, path:str) -> str | None:
        """Looks for a existing template and returns the path to it
        
        If no config file was found, None is returned"""
        path_to_file, file_name = split(path)
        file_name = file_name.split(".")[0]
        path_to_temp = Path(path_to_file) / f".{file_name}.template"

        return path_to_temp
    
    def __has_all_template_options(self, template:configparser.ConfigParser):
        """Check if config contains all sections and options from the template"""
        for section in template.sections():
            if section not in self:
                return False
            template_options = set(template.options(section))
            config_options = set(config.options(section))
            if not template_options.issubset(config_options):
                return False
        return True

    def set(self, section: str, option: str, value: str | None = None) -> None:
        old_value = self.get(section, option, fallback=None)
        if old_value:
            self.__logger.debug(f"New value in section '{section}' at option '{option}' added: '{value}'")
            self.__pending_changes += 1
        else:
            if self.has_option(section, option):
                self.__logger.debug(f"Value in section '{section}' at option '{option}' changed: '{old_value}' -> '{value}'")
            if old_value != value:
                self.__pending_changes += 1
        
        return super().set(section, option, value)
    
    def remove_option(self, section, option):
        if self.has_option(section, option):
            value = self.get(section, option)
            self.__logger.debug(f"Option removed in section '{section}' for '{option}': '{value}'")
            self.__pending_changes += 1
        
        return super().remove_option(section, option)
    
    def remove_section(self, section):
        if self.has_section(section):
            self.__logger.info(f"Section removed: '{section}'")
            self.__pending_changes += 1

        return super().remove_section(section)
    
    def save(self):
        """Saves changes to disk"""
        with open(self.__file_path, 'w') as configfile:
            self.write(configfile)
        self.__logger.debug(f"Contents ({self.__pending_changes} changes) have been saved to disk")

    def get_config_file_path(self) -> str:
        """Returns the path to the config file"""
        return self.__file_path
    
    def get_template_file_path(self) -> str:
        """Returns the path to the template file, a config could be created from
        
        Returns None if the is no template file"""
        return self.__template_path
    
    def compare_to_template(self) -> str:
        """Returns one of multiple possible keywords depending on the relation of both files

        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Return Keyword  |                                                       Description                                                        |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | not_found       | No template file found                                                                                                   |
        | equal           | Both files contain the same sections and options                                                                         |
        | config_plus     | Config contains additional sections and/or options compared to template                                                  |
        | config_options  | Config contains additional options but same sections                                                                     |
        | config_base     | Same as "config_plus" but additionally config contains all sections and options from the template                        |
        | config_minus    | Config contains fewer sections and/or options as template                                                                |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+"""

        # Check existence of template
        if self.__template_path == None:
            return "not_found"
        
        template_config = configparser.ConfigParser()
        template_config.read_file(open(self.__template_path))
        config_sections = set(self.sections())
        template_sections = set(template_config.sections())

        # Check if config contains all the same (or more) sections than template
        same_or_more_sections = config_sections >= template_sections

        # Check if both files have the same amount of sections
        same_amount_of_sections = len(config_sections) == len(template_sections)

        # Consolidate the options of both files
        all_config_options = set()
        all_template_options = set()
        all_sections = config_sections.union(template_sections)
        config_all_present = True
        template_all_present = True
        for section in all_sections:
            try:
                for option in self.options(section):
                    all_config_options.add(f"{section}.{option}")
            except configparser.NoSectionError:
                config_all_present = False
                
            try:
                for option in template_config.options(section):
                    all_template_options.add(f"{section}.{option}")
            except configparser.NoSectionError:
                template_all_present = False

        # Check if both have the same options
        same_or_more_options = all_config_options >= all_template_options

        # Check if both have the same amount of options
        same_amount_of_options = len(all_config_options) == len(all_template_options)

        # Check for different cases
        # Since both files have the same (or more) options (and the options contain the section name) and contain the same amount, they must be equal
        if same_or_more_options and same_amount_of_options:
            return "equal"
        
        # Since the config contains not even the same sections as present in the template, it doesn't contain the same base options
        if not same_or_more_sections:
            return "config_minus"
        
        # If the config contains more sections or options than the template
        if same_or_more_sections:
            if same_or_more_options:
                # If config contains all sections and options from template but also has extras
                return "config_base"
            else:
                # Config has extra sections and/or options, but not necessarily all from template
                return "config_plus"
        
        # If the config contains the same sections but additional options within those sections
        if same_amount_of_sections and not same_amount_of_options:
            return "config_options"
        
        return "config_plus"

    def created_from_template(self) -> bool:
        """Will ONLY return `True` if the config file has been created from template at the first run"""
        return self.__from_template
    
    def check_for_update(self, omit_save:bool = False):
        """Updates the already created config to the same level as the template, 
        
        no options are deleted or their values changed."""
        if self.__template_path == None:
            raise FileNotFoundError
        template_config = configparser.ConfigParser()
        template_config.read_file(open(self.__template_path))

        updated_options = 0
        for section in template_config.sections():
            options = template_config.options(section)

            for option in options:
                if not self.has_option(section, option):
                    self.set(section, option, template_config.get(section, option))
                    updated_options += 1

        if updated_options:
            _, file_name = split(self.__file_path)
            self.__logger.error(f"The confg updated at {updated_options} locations, you might want check the {file_name} for unchanged placeholders")
            
            if not omit_save:
                self.save()

if __name__ == "__main__":
    # Dummy logger
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger = logging.getLogger("utils")
    logger.addHandler(console)
    logger.setLevel(logging.DEBUG)

    file_path = Path(__file__).resolve()

    base_path = file_path.parents[2]
    print(f"Base path of the program: {base_path}")

    config = Advanced_ConfigParser(Path.joinpath(base_path, "config", "bot.ini"))
    print(config.compare_to_template())
    # config["DEFAULT"]["Compression"] = "no"
    # config.save()