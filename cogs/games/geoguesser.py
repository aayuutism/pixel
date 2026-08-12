import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from cogs.games.flags import FLAGS

class StopGameView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=30.0) # Match the question timeout
        self.author_id = author_id
        self.stopped = False

    @discord.ui.button(label="Stop Game", style=discord.ButtonStyle.danger, emoji="🛑")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This isn't your game session!", ephemeral=True)
        
        self.stopped = True
        self.stop()
        button.disabled = True
        await interaction.response.edit_message(view=self)

class FlagGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="geoguesser", description="Guess flags continuously until you miss or stop!")
    async def flag_guesser(self, interaction: discord.Interaction):
        score = 0
        game_active = True
        
        await interaction.response.defer()

        while game_active:
            country, (image_url, valid_answers) = random.choice(list(FLAGS.items()))

            view = StopGameView(author_id=interaction.user.id)

            embed = discord.Embed(
                title=f"Guess the Flag! (Score: {score})",
                description="Type your answer in this channel within 30 seconds!\nClick **Stop Game** below anytime to exit.",
                color=discord.Color.blue()
            )
            embed.set_image(url=image_url)

            await interaction.followup.send(embed=embed, view=view)

            def check(m: discord.Message):
                return (
                    m.channel.id == interaction.channel_id
                    and not m.author.bot
                    and m.content.strip().lower() in valid_answers
                )

            try:
                # Wait for the user's message answer
                winner = await self.bot.wait_for("message", check=check, timeout=30.0)
                
                # Check if the player clicked Stop before/during answering
                if view.stopped:
                    await interaction.followup.send(f"🛑 Game ended by **{interaction.user.display_name}**! Final Score: **{score}**.")
                    break

                score += 1
                await interaction.followup.send(
                    f"🎉 Correct, {winner.author.mention}! It was **{country}**! (+1 Point)"
                )
                await asyncio.sleep(2)

            except asyncio.TimeoutError:
                # Handle stop button vs actual time expiration
                if view.stopped:
                    await interaction.followup.send(f"🛑 Game ended by **{interaction.user.display_name}**! Final Score: **{score}**.")
                else:
                    await interaction.followup.send(
                        f"⏰ Time's up! The correct answer was **{country}**.\nGame Over! Final Score: **{score}**."
                    )
                game_active = False

async def setup(bot):
    await bot.add_cog(FlagGame(bot))
