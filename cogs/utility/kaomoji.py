import random
import discord
from discord.ext import commands
from discord import app_commands

from data.kaomojis import KAOMOJI_LIST 

class KaomojiCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kaomoji", description="Get a random kaomoji!")
    @app_commands.describe(
        emotion="Optional category for the kaomoji"
    )
    @app_commands.choices(emotion=[
        app_commands.Choice(name="Classic", value="classic"),
        app_commands.Choice(name="Smile", value="smile"),
        app_commands.Choice(name="Love", value="love"),
        app_commands.Choice(name="Flex", value="flex"),
        app_commands.Choice(name="Animal", value="animal"),
        app_commands.Choice(name="Surprise", value="surprise"),
        app_commands.Choice(name="Cry", value="cry"),
        app_commands.Choice(name="Angry", value="angry"),
        app_commands.Choice(name="Bored", value="bored"),
        app_commands.Choice(name="Nervous", value="nervous"),
    ])
    async def kaomoji(
        self, 
        interaction: discord.Interaction, 
        emotion: app_commands.Choice[str] = None
    ):
        if emotion:
            category = emotion.value
            kaomoji_choice = random.choice(KAOMOJI_LIST[category])
        else:
            all_kaomojis = [k for sublist in KAOMOJI_LIST.values() for k in sublist]
            kaomoji_choice = random.choice(all_kaomojis)

        await interaction.response.send_message(kaomoji_choice)

async def setup(bot: commands.Bot):
    await bot.add_cog(KaomojiCog(bot))
