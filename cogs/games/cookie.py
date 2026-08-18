import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

games_group = app_commands.Group(name="games", description="Play various mini-games!")

class CookieGameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=15.0)
        self.winner: discord.User | None = None

    @discord.ui.button(emoji="🍪", style=discord.ButtonStyle.success)
    async def cookie_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = interaction.user
        button.disabled = True
        self.stop()
        
        # Announce the winner
        await interaction.response.edit_message(
            content=f"🎉 {interaction.user.mention} clicked the cookie first! 🍪",
            view=self
        )

class CookieCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @games_group.command(name="cookie", description="Click the cookie first!")
    async def cookie(self, interaction: discord.Interaction):
        # 1. Initial prompt
        await interaction.response.send_message("Get ready... Click the cookie soon!")
        
        # 2. Random countdown delay (between 2 to 5 seconds)
        delay = random.randint(2, 5)
        
        for countdown in range(delay, 0, -1):
            await asyncio.sleep(1)
            await interaction.edit_original_response(
                content=f"Get ready... Click the cookie in **{countdown}**"
            )

        # 3. Spawn the button & change message text
        view = CookieGameView()
        await interaction.edit_original_response(
            content="**Click the cookie! 🍪**",
            view=view
        )

        # 4. Wait for someone to click or time out
        await view.wait()

        # If no one clicked before timeout
        if view.winner is None:
            for child in view.children:
                child.disabled = True
            await interaction.edit_original_response(
                content="⏰ Nobody clicked the cookie in time!",
                view=view
            )

async def setup(bot):
    if not bot.tree.get_command("games"):
        bot.tree.add_command(games_group)
    await bot.add_cog(CookieCog(bot))
