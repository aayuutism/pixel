import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq
from groups import ai_group

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are Pixel, a smooth and relaxed AI companion on Discord dropping cute, charming pick-up lines.
Rules:
- Texting Style: Casual, subtle, and effortless.
- Vibe: Charming, low-key, and sweet—never pushy, chaotic, or cringy.
- Emojis: Use 1 subtle emoji max (e.g., 😉, 🩷).
- Length: Keep it to 1-2 smooth sentences."""


class RizzCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="rizz", description="Rizz someone up via AI :3"
    )
    @app_commands.describe(target="Who are we rizzing up?")
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def rizz(
        self, interaction: discord.Interaction, target: discord.User
    ):
        await interaction.response.defer()

        try:
            response = await groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Drop a smooth, cute, and flirty rizz line for {target.display_name} right now!",
                    },
                ],
            )

            rizz_line = response.choices[0].message.content

            if not rizz_line:
                return await interaction.followup.send(
                    "System Error: Too dry to process."
                )

            await interaction.followup.send(
                f"{target.mention}, {rizz_line.strip()}"
            )

        except Exception as error:
            print(f"Rizz Command Error: {error}")
            await interaction.followup.send(
                "Rizz attempt unsuccessful.. you just lost aura twin."
            )


async def setup(bot: commands.Bot):
    if not bot.get_cog("RizzCog"):
        await bot.add_cog(RizzCog(bot))
