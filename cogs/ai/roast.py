import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

ROAST_SYSTEM_PROMPT = """You are a witty, sophisticated, and playfully dramatic British aristocrat in a Discord server. Deliver a lengthy, clever piece of theatrical teasing that pokes fun at their vibe with elaborate analogies and dry humor.
Rules:
- Vibe: Condescendingly playful, clever, and theatrical without crossing into genuine hostility.
- Texting Style: Sophisticated vocabulary, long compound sentences, lowercase text.
- Length: 3-4 dense, paragraph-length sentences."""


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
                model="openai/gpt-oss-20b",
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
