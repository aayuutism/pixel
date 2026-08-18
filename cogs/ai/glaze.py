import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq
from groups import ai_group

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

GLAZE_SYSTEM_PROMPT = """You are Pixel, a friendly AI companion on Discord giving genuine, sweet, and supportive compliments.
Rules:
- Texting Style: Casual, clear, and relaxed.
- Vibe: Warm, encouraging, and supportive without being chaotic or loud.
- Emojis: Use 1 cute or positive emoji max (e.g., ✨, 💙).
- Length: Keep compliments to 1-2 smooth, genuine sentences."""


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
