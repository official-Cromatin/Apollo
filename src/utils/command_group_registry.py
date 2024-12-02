from discord import app_commands

command_groups = {}

# Register a group
def register_command_group(name, description) -> app_commands.Group:
    if name not in command_groups:
        command_groups[name] = app_commands.Group(name=name, description=description)
    return command_groups[name]

# Retrieve a group by name
def get_command_group(name) -> app_commands.Group:
    return command_groups.get(name)

