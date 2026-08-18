import discord
from discord.ext import commands
from discord import app_commands
import pyfiglet

class AsciiCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="asciify", description="Convert text to ASCII art")
    @app_commands.describe(
        text="The text you want to convert to ASCII",
        font="The font you want to use for the ASCII"
    )
    # Add preset choices for the slash command dropdown
    @app_commands.choices(font=[
        app_commands.Choice(name="3d_diagonal (Default)", value="3d_diagonal"),
        app_commands.Choice(name="3d-ascii", value="3d-ascii"),
        app_commands.Choice(name="5lineoblique", value="5lineoblique"),
        app_commands.Choice(name="avatar", value="avatar"),
        app_commands.Choice(name="braced", value="braced"),
        app_commands.Choice(name="cards", value="cards"),
        app_commands.Choice(name="computer", value="computer"),
        app_commands.Choice(name="drpepper", value="drpepper"),
        app_commands.Choice(name="fun_face", value="fun_face"),
        app_commands.Choice(name="keyboard", value="keyboard"),
        app_commands.Choice(name="konto_slant", value="konto_slant"),
    ])
    async def asciify(
        self, 
        interaction: discord.Interaction, 
        text: str, 
        font: app_commands.Choice[str] = None
    ):
        # Default to 3d_diagonal if no choice was picked
        selected_font = font.value if font else "3d_diagonal"

        try:
            # Generate ASCII art
            ascii_art = pyfiglet.figlet_format(text, font=selected_font)
            
            if len(ascii_art) > 1990:
                await interaction.response.send_message("⚠️ The output ASCII art is too large for Discord!")
                return

            await interaction.response.send_message(f"```\n{ascii_art}\n```")

        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to generate ASCII art: `{str(e)}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(AsciiCog(bot))
