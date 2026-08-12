import discord
from discord.ext import commands
from discord import app_commands
import pyfiglet

# Allowed fonts list matching your screenshot
VALID_FONTS = [
    "3d-ascii", "3d_diagonal", "5lineoblique", "avatar", 
    "braced", "cards", "computer", "drpepper", 
    "fun_face", "keyboard", "konto_slant"
]

class AsciiCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="asciify", description="Convert text to ASCII art")
    @app_commands.describe(
        text="The text you want to convert to ASCII",
        font="The font you want to use for the ASCII"
    )
    async def asciify(
        self, 
        interaction: discord.Interaction, 
        text: str, 
        font: str = "3d_diagonal"
    ):
        font_clean = font.lower().strip()

        # Validate font selection
        if font_clean not in VALID_FONTS:
            fonts_list_str = ", ".join(VALID_FONTS)
            error_msg = f"⚠️ {interaction.user.mention}: Invalid font. Available fonts are: {fonts_list_str}"
            await interaction.response.send_message(error_msg)
            return

        try:
            # Generate ASCII art
            ascii_art = pyfiglet.figlet_format(text, font=font_clean)
            
            # Discord message character limit check
            if len(ascii_art) > 1990:
                await interaction.response.send_message("⚠️ The output ASCII art is too large for Discord!")
                return

            # Send result wrapped in codeblock for monospace rendering
            await interaction.response.send_message(f"```\n{ascii_art}\n```")

        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to generate ASCII art: `{str(e)}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(AsciiCog(bot))
