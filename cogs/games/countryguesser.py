from __future__ import annotations

import random
import discord
from discord import app_commands
from discord.ext import commands

# Import your custom flags dictionary from cogs/games/flags.py
from .flags import FLAGS


class CountryGuesserCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="countryguesser",
        description="Guess the country!",
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def countryguesser(self, interaction: discord.Interaction):
        # Pick a random country from your FLAGS dictionary
        random_country = random.choice(list(FLAGS.keys()))
        flag_url, _ = FLAGS[random_country]

        embed = discord.Embed(
            description="### Type your guess below!",
            color=discord.Color.from_rgb(47, 49, 54),
        )
        embed.set_image(url=flag_url)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    if not bot.get_cog("CountryGuesserCog"):
        await bot.add_cog(CountryGuesserCog(bot))
