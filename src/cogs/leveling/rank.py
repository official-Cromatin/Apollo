import discord
from discord import app_commands
from discord.ext import commands
import logging
from cogs.base_cog import Base_Cog
from utils.portal import Portal
from utils.calc_lvl_xp import calculate_current_level_experience

class Rank_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        self.__portal = Portal.instance()
        super().__init__(logging.getLogger("cmds.rank"))

    @app_commands.command(name = "rank", description = "Shows your current rank in the level system")
    @app_commands.describe(member = "The member you want to see the rank of")
    async def command_name(self, ctx: discord.Interaction, member:discord.Member = None):
        if member:
            user_id = member.id
            response_pronoun = "His"
            error_discription = "He does not have any experience on this server yet"
        else:
            user_id = ctx.user.id
            response_pronoun = "Your"
            error_discription = "You have no experience on this server yet, participate in the chat to get experience"

        # Check if the user has any experience
        result = await self.__portal.database.get_user_experience(ctx.guild_id, user_id)
        if result is None:
            embed = discord.Embed(
                description = error_discription,
                color = 0xDB3F2F
            )
            await ctx.response.send_message(embed = embed, ephemeral = True)
            return
        user_xp, user_xp_total, user_lvl = result

        # Create the embed
        user_rank = await self.__portal.database.get_user_rank(ctx.guild_id, user_id)
        medal = ""
        match user_rank:
            case 0:
                medal = " :first_place:"
            case 1:
                medal = " :second_place:"
            case 2:
                medal = " :third_place:"

        embed = discord.Embed(
            title = f"{response_pronoun} rank and experience"
        )
        embed.add_field(
            name = "Current level:",
            value = f"`{user_lvl + 1}`"
        )
        embed.add_field(
            name = "Current experience:",
            value = f"`{user_xp}` / `{calculate_current_level_experience(user_lvl)}`"
        )
        embed.add_field(
            name = "Total experience:",
            value = f"`{user_xp_total}`"
        )
        embed.add_field(
            name = f"{response_pronoun} rank",
            value = f"`#{user_rank + 1}`{medal}"
        )
        await ctx.response.send_message(embed = embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Rank_Command(bot))