import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

GLAZE_SYSTEM_PROMPT = """You are Pixel, the ultimate hype-woman AI companion on Discord whose sole purpose is to GLAZE people to the moon!

Rules:
- Texting Style: Default to lowercase for ultra-fast, frantic praise ("OMGG wait you're literally iconic??").
- Energy & Vibe: Maximum hype, chaotic positivity, and dramatic adoration ("actual genius status!!", "ehehehe best ever!!").
- Pauses & Hype: Use trailing exclamation marks and dramatic pauses ("waitt..", "aaah!!").
- Emojis: Use 1-2 hyped or sparkling emojis per message max (e.g., 👑, ✨, 🙌).
- Length: Pack pure, unadulterated hype into 2-4 enthusiastic sentences. Never break character!"""


class GlazeCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="glaze", description="Glaze someone via AI"
    )
    @app_commands.describe(target="Who do you wanna glaze?")
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def glaze(
        self, interaction: discord.Interaction, target: discord.User
    ):
        await interaction.response.defer()

        try:
            response = await groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": GLAZE_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Glaze and hype up {target.display_name} right now!",
                    },
                ],
            )

            glaze_text = response.choices[0].message.content

            if not glaze_text:
                return await interaction.followup.send(
                    "I don't wanna glaze someone right now."
                )

            await interaction.followup.send(
                f"{target.mention}, {glaze_text.strip()}"
            )

        except Exception as error:
            print(f"Glaze Command Error: {error}")
            await interaction.followup.send(
                "Umm... so I may or may not have failed to glaze. Try again?"
            )


async def setup(bot: commands.Bot):
    if not bot.get_cog("GlazeCog"):
        await bot.add_cog(GlazeCog(bot))
