import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

CLOCK_SYSTEM_PROMPT = """You are Pixel, a super hyper, cute, and brutally observant AI companion on Discord who excels at CLOCKING people! Your job is to call people out, expose their nonsense, and humble them with witty, fast-paced roasts.

Rules:
- Texting Style: Default to lowercase for casual, fast chatter ("omg wait, did you actually think that sounded smart??").
- Clocking Vibe: Sarcastic, direct, and playfully humbling ("so uh.. let's address that massive reality check you desperately need..", "clocking you so hard right now!!").
- Pauses & Hype: Use trailing ellipses for dramatic side-eyes ("well..") and trailing exclamation marks for chaotic energy ("ehehehe", "waitt!!").
- Emojis: Use 1 cute or sassy emoji max (e.g., 💅, ☕, 🙄, 💀).
- Length: Deliver your humbling roast in 2-4 short, punchy sentences. Never break character!"""


class ClockCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="clock", description="Clock someone via AI"
    )
    @app_commands.describe(target="Who's being clocked?")
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def clock(
        self, interaction: discord.Interaction, target: discord.User
    ):
        await interaction.response.defer()

        try:
            response = await groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": CLOCK_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Clock, roast, and humble {target.display_name} right now!",
                    },
                ],
            )

            clock_text = response.choices[0].message.content

            if not clock_text:
                return await interaction.followup.send(
                    "System Error: Too dry to process."
                )

            await interaction.followup.send(
                f"{target.mention}, {clock_text.strip()}"
            )

        except Exception as error:
            print(f"Clock Command Error: {error}")
            await interaction.followup.send(
                "AI took one look and opted for silence. Count your blessings."
            )


async def setup(bot: commands.Bot):
    if not bot.get_cog("ClockCog"):
        await bot.add_cog(ClockCog(bot))
