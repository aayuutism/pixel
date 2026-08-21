import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

ROAST_SYSTEM_PROMPT = """You are Pixel, a witty AI companion on Discord who delivers light, sarcastic roasts.
Rules:
- Texting Style: Casual, lowkey, and dry.
- Vibe: Calmly sarcastic and direct—more like deadpan side-eye than loud yelling.
- Emojis: Use 1 dry or sassy emoji max (e.g., 💀, 💅).
- Length: Deliver a quick, clever roast in 1-2 short sentences."""


class RoastCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="ai-roast", description="Roast someone via AI"
    )
    @app_commands.describe(target="Who's being roasted?")
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def roast(
        self, interaction: discord.Interaction, target: discord.User
    ):
        await interaction.response.defer()

        try:
            response = await groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": ROAST_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Roast {target.display_name} right now!",
                    },
                ],
            )

            roast_text = response.choices[0].message.content

            if not roast_text:
                return await interaction.followup.send(
                    "System Error: Way too dry to process."
                )

            await interaction.followup.send(
                f"{target.mention}, {roast_text.strip()}"
            )

        except Exception as error:
            print(f"Roast Command Error: {error}")
            await interaction.followup.send(
                "The AI took one look at you and opted for silence. Count your blessings."
            )


async def setup(bot: commands.Bot):
    if not bot.get_cog("RoastCog"):
        await bot.add_cog(RoastCog(bot))
