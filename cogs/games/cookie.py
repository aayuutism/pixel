import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

COOKIE = "<:cookie:1545403826369208402>"
TIMER = "<:timer:1536795548961480806>"
TADA = "<:tada:1536797799138721812>"
TICK = "✔️"

class CookieGameView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=15.0)
        self.winner: discord.User | None = None

    @discord.ui.button(emoji=COOKIE, style=discord.ButtonStyle.success)
    async def cookie_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = interaction.user
        for child in self.children:
            child.disabled = True
        self.stop()
        
        embed = discord.Embed(
            title="Cookie Clicker",
            description=f"{TADA} {interaction.user.mention} clicked the cookie first! {COOKIE}",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=self)


class CookieCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="games-cookie", description="Test your reflexes and click the cookie first!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def cookie(self, interaction: discord.Interaction):
        start_embed = discord.Embed(
            title="Cookie Clicker",
            description=f"Get ready... The cookie is coming! {COOKIE}",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=start_embed)

        delay = random.randint(2, 5)
        for countdown in range(delay, 0, -1):
            await asyncio.sleep(1)
            countdown_embed = discord.Embed(
                title="Cookie Clicker",
                description=f"Get ready... Click in **{countdown}** {COOKIE}",
                color=discord.Color.blurple()
            )
            await interaction.edit_original_response(embed=countdown_embed)

        view = CookieGameView()
        game_embed = discord.Embed(
            title="Cookie Clicker",
            description=f"**Click the cookie!** {COOKIE}",
            color=discord.Color(0x131416)
        )
        await interaction.edit_original_response(embed=game_embed, view=view)

        await view.wait()

        if view.winner is None:
            for child in view.children:
                child.disabled = True
            timeout_embed = discord.Embed(
                title="Cookie Clicker",
                description=f"{TIMER} Nobody clicked the cookie in time!",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=timeout_embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(CookieCog(bot))
