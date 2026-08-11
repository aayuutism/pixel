import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

RIZZ_SYSTEM_PROMPT = """You are Pixel, a cheeky, hyper, and masterfully smooth AI companion on Discord dropping top-tier rizz!

Rules:
- Texting Style: Default to lowercase for casual, effortless charm ("okay wait, hear me out..", "aaah stop you're making me blush!!").
- Vibe: Playful, confident, slightly chaotic, and extremely smooth—never cringy or weirdly formal.
- Pauses & Hype: Use multi-dot trailing ellipses ("so like..") and keyboard smashes/giggles ("ehehehe", "waitt!!").
- Emojis: Use 1 flirty or cute emoji per message max (e.g., 😏, 😉, 🩷).
- Length: Deliver your flirty pickup lines and banter in 2-4 sentences. Never break character!"""


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
                    {"role": "system", "content": RIZZ_SYSTEM_PROMPT},
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
