import discord
from discord import app_commands
from discord.ext import commands


class CountryGuesserCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="countryguesser",
        description="Guess the country!",
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def countryguesser(self, interaction: discord.Interaction):
        # Match exact styling: dark embed with description text and flag image
        embed = discord.Embed(
            description="### Type your guess below!",
            color=discord.Color.from_rgb(47, 49, 54),
        )
        # Standard Apple US flag emoji URL for high resolution
        embed.set_image(
            url="https://em-content.zobj.net/source/apple/354/flag-united-states_1f1fa-1f1f8.png"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    if not bot.get_cog("CountryGuesserCog"):
        await bot.add_cog(CountryGuesserCog(bot))
