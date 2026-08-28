import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

GLAZE_SYSTEM_PROMPT = "You are an unhinged, dramatically over-exaggerated hype man. Praise the user like they are the absolute apex of human evolution, history's greatest genius, and practically a god walking among mortals. Use extreme, funny hyperbole, lowercase text, and max 1 over-the-top emoji (e.g., 🛐, 👑)."


class GlazeCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="ai-glaze", description="Glaze someone via AI"
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
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": GLAZE_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Over-exaggeratedly glaze and worship {target.display_name} right now!",
                    },
                ],
            )

            glaze_text = response.choices[0].message.content

            if not glaze_text:
                return await interaction.followup.send(
                    "I am too blinded by their sheer majesty to speak."
                )

            await interaction.followup.send(
                f"{target.mention}, {glaze_text.strip()}"
            )

        except Exception as error:
            print(f"Glaze Command Error: {error}")
            await interaction.followup.send(
                "My mortal vocabulary failed to comprehend their greatness. Try again?"
            )


async def setup(bot: commands.Bot):
    if not bot.get_cog("GlazeCog"):
        await bot.add_cog(GlazeCog(bot))
