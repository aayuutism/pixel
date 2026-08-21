import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

class CookieGameView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=15.0)
        self.winner: discord.User | None = None

    @discord.ui.button(emoji="🍪", style=discord.ButtonStyle.success)
    async def cookie_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = interaction.user
        button.disabled = True
        self.stop()
        
        await interaction.response.edit_message(
            content=f"🎉 {interaction.user.mention} clicked the cookie first! 🍪",
            view=self
        )


class CookieCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="games-cookie", description="Test your reflexes and click the cookie first!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def cookie(self, interaction: discord.Interaction):
        await interaction.response.send_message("Get ready... The cookie is coming!")

        delay = random.randint(2, 5)
        for countdown in range(delay, 0, -1):
            await asyncio.sleep(1)
            await interaction.edit_original_response(content=f"Get ready... Click in **{countdown}**")

        view = CookieGameView()
        await interaction.edit_original_response(content="**Click the cookie! 🍪**", view=view)

        await view.wait()

        if view.winner is None:
            for child in view.children:
                child.disabled = True
            await interaction.edit_original_response(
                content="⏰ Nobody clicked the cookie in time!", view=view
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(CookieCog(bot))
