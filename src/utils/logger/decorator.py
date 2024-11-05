from functools import wraps
import discord

def log_command_execution(func):
    """Wraps an command function to print execution logs to the console"""
    @wraps(func)
    async def wrapper(self, interaction:discord.Interaction, *args, **kwargs):
        self._logger.debug(f"User {interaction.user} in channel {interaction.channel} on guild {interaction.guild} executed the {func.__name__} command")

        return await func(self, interaction, *args, **kwargs)
    return wrapper
