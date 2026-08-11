import os
import discord
from discord import app_commands
from discord.ext import commands
from groq import AsyncGroq

# Initialize AsyncGroq client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


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
                    {
                        "role": "user",
                        "content": (
                            "Generate a sharp, witty, articulate call-out to clock someone with high-IQ banter. Output ONLY the text of the clock itself, nothing else."
                        ),
                    }
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
    await bot.add_cog(ClockCog(bot))
