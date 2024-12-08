import discord
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import Base_Cog

import logging
from datetime import datetime
from utils.datetime_tools import get_elapsed_time_milliseconds
import traceback
from utils.truncate_str import truncate_message_with_notice

class Reload_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__cached_cog_names:list[str] = None
        self.__reload_running = False
        super().__init__(logging.getLogger("cmds.reload"))

    async def autocomplete_cog(self, ctx: discord.Interaction, cog_name_stw:str):
        """Helpermethod to recommend the right cog name to the user"""
        # Cache the cog names if not cached yet
        if not self.__cached_cog_names:
            self.__cached_cog_names = list(self.__bot.extensions.keys())

        if cog_name_stw == "":
            # Return first 25 cog names, if provided name is empty
            matching_cogs = sorted(self.__cached_cog_names)
        else:
            matching_cogs = []
            for cog_name in self.__cached_cog_names:
                if cog_name.startswith(cog_name_stw.lower()):
                    matching_cogs.append(cog_name)
        
        choices = []
        for matching_cog in matching_cogs[:25]:
            choices.append(app_commands.Choice(name = matching_cog.removeprefix("cogs.").capitalize(), value = matching_cog))

        return choices

    @app_commands.command(name = "reload_all", description = "Reloads all cogs")
    async def reload_all(self, ctx: discord.Interaction):
        if self.__reload_running:
            await ctx.response.send_message("Reload is allready being executed", ephemeral = True)
        else:
            self.__reload_running = True
            task_start = datetime.now().timestamp()
            cog_names = list(self.__bot.extensions.keys())
            self._logger.debug(f"Reloading all {len(cog_names)} cogs ...")
            try: 
                embed_cog_stats = "Reloaded the following cogs:\n"
                for extension_name in cog_names:
                    start_reload = datetime.now().timestamp()
                    await self.__bot.reload_extension(extension_name)
                    embed_cog_stats += f"- {extension_name.removeprefix('cogs.').capitalize()} (`{get_elapsed_time_milliseconds(datetime.now().timestamp() - start_reload)}`)\n"

            except Exception as error:
                embed_cog_stats += f"- {extension_name.removeprefix('cogs.').capitalize()} <--"
                traceback_str = truncate_message_with_notice(traceback.format_exc(), 1800, "\nSee console for more details on the full traceback")

                embed = discord.Embed(
                    title = "Reloading All Cogs",
                    description = f"{embed_cog_stats} \n\nDuring the reload the following exception occured:\n```{traceback_str}```",
                    color = 0xED4337)

                raise error
            else:
                elapsed_time = get_elapsed_time_milliseconds(datetime.now().timestamp() - task_start)
                embed = discord.Embed(
                    title = "Reloading All Cogs",
                    description = f"{embed_cog_stats}Total time spend: `{elapsed_time}`",
                    color = 0x4BB543)

                self._logger.info(f"Cogs successfully reloaded after {elapsed_time}")
            finally:
                await ctx.response.send_message(embed = embed, ephemeral = True)
                self.__reload_running = False
        

    @app_commands.command(name = "reload", description = "Reload specific cog")
    @app_commands.autocomplete(cog_name = autocomplete_cog)
    async def reload(self, ctx: discord.Interaction, cog_name:str):
        if self.__reload_running:
            await ctx.response.send_message("Reload is allready being executed", ephemeral = True)
        else:
            self.__reload_running = True
            task_start = datetime.now().timestamp()
            self._logger.debug(f"Reloading {cog_name} cog ...")
            try:
                await self.__bot.reload_extension(cog_name)
            except Exception as error:
                traceback_str = truncate_message_with_notice(traceback.format_exc(), 1800, "\nSee console for more details on the full traceback")
                embed = discord.Embed(
                    title = f"Reloading `{cog_name.removeprefix('cogs.').capitalize()}` cog",
                    description = f"Reload failed with the following exception:\n```{traceback_str}```",
                    color = 0xED4337)

                raise error
            else:
                embed = discord.Embed(
                    title = f"Reloading `{cog_name.removeprefix('cogs.').capitalize()}` cog",
                    description = f"Total time spend: `{get_elapsed_time_milliseconds(datetime.now().timestamp() - task_start)}`",
                    color = 0x4BB543)

                self._logger.info(f"Cog {cog_name} successfully reloaded after {get_elapsed_time_milliseconds(datetime.now().timestamp() - task_start)}")
            finally:
                await ctx.response.send_message(embed = embed, ephemeral = True)
                self.__reload_running = False
            
            # Clear the cache
            self.__cached_cog_names = None

async def setup(bot:commands.Bot):
    await bot.add_cog(Reload_Command(bot))