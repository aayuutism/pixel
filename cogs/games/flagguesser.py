import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from cogs.games.flags import FLAGS

class FlagGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="flagguesser", description="Guess the flag of a random country!")
    async def flag_guesser(self, interaction: discord.Interaction):
        # 1. Select a random flag
        country, (image_url, valid_answers) = random.choice(list(FLAGS.items()))

        # 2. Build the game embed
        embed = discord.Embed(
            title="Guess the Flag!",
            description="Type your answer in this channel within 15 seconds!",
            color=discord.Color.blue()
        )
        embed.set_image(url=image_url)

        # 3. Send initial reply
        await interaction.response.send_message(embed=embed)

        # 4. Check function for incoming channel messages
        def check(message: discord.Message):
            return (
                message.channel.id == interaction.channel_id
                and not message.author.bot
                and message.content.strip().lower() in valid_answers
            )

        # 5. Wait for the player's response
        try:
            winner = await self.bot.wait_for("message", timeout=15.0, check=check)
            await interaction.followup.send(
                f"🎉 Correct, {winner.author.mention}! The country was **{country}**."
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                f"⏰ Time's up! The correct answer was **{country}**."
            )

async def setup(bot):
    await bot.add_cog(FlagGame(bot))
