import discord
from discord import app_commands
from discord.ext import commands

# Define the central /games slash command group
games_group = app_commands.Group(
    name="games", 
    description="Play various mini-games!"
)


class Games(commands.Cog):
    """Central Cog managing the /games parent group."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    # Ensure the parent group command is added to the bot's app command tree
    if not bot.tree.get_command("games"):
        bot.tree.add_command(games_group)

    await bot.add_cog(Games(bot))
