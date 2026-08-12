from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class GameControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Quit Game",
        style=discord.ButtonStyle.danger,
        custom_id="cg_quit_btn",
    )
    async def quit_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # UI Placeholder action
        await interaction.response.send_message("Game ended!", ephemeral=True)

    @discord.ui.button(
        label="Hint",
        style=discord.ButtonStyle.secondary,
        custom_id="cg_hint_btn",
    )
    async def hint_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # UI Placeholder action
        await interaction.response.send_message("Here is a hint!", ephemeral=True)


class CountryGuesserCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def build_embed(self, flag_url: str) -> discord.Embed:
        embed = discord.Embed(
            title="Guess the country!",
            description="Which country does this flag belong to?",
            color=discord.Color.from_rgb(47, 49, 54),
        )
        embed.set_image(url=flag_url)
        embed.set_footer(text="Type your answer down below!")
        return embed

    @app_commands.command(
        name="countryguesser",
        description="Preview the flag guesser interface!",
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def countryguesser(self, interaction: discord.Interaction):
        # Dummy URL for UI testing
        sample_flag_url = "https://flagcdn.com/w640/jp.png"

        embed = self.build_embed(sample_flag_url)
        view = GameControlView()

        # Responds with the embed UI directly
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    if not bot.get_cog("CountryGuesserCog"):
        await bot.add_cog(CountryGuesserCog(bot))
