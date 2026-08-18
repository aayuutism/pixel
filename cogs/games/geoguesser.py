import random
import asyncio
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from data.flags import FLAGS

# Reuse the shared group if it exists, or create it if this file runs standalone
if not 'games_group' in globals():
    games_group = app_commands.Group(name="games", description="Play various mini-games!")

class GameView(discord.ui.View):
    def __init__(self, author_id: int, country_name: str):
        super().__init__(timeout=30.0)
        self.author_id = author_id
        self.country_name = country_name
        self.stopped = False
        self.hint_used = False

    @discord.ui.button(label="Hint", style=discord.ButtonStyle.primary)
    async def hint_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This isn't your game, silly!", ephemeral=True)
        
        if self.hint_used:
            return await interaction.response.send_message("A hint has already been used for this round!", ephemeral=True)

        self.hint_used = True
        button.disabled = True
        await interaction.response.edit_message(view=self)

        # Format hint: e.g. "I _ _ _ _ _ _" and length
        first_letter = self.country_name[0].upper()
        masked_name = first_letter + "".join(" _ " if char.isalpha() else char for char in self.country_name[1:])
        
        hint_msg = f"💡 **Hint:** Starts with **{first_letter}** ({len(self.country_name)} letters)\nPattern: `{masked_name}`"
        await interaction.followup.send(hint_msg)

    @discord.ui.button(label="End Game", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("This isn't your game, silly!", ephemeral=True)
        
        self.stopped = True
        self.stop()
        button.disabled = True
        await interaction.response.edit_message(view=self)

class FlagGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @games_group.command(name="geoguesser", description="Guess the countries by their flags!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def flag_guesser(self, interaction: discord.Interaction):
        score = 0
        wrong_attempts = 0
        max_wrong = 5
        game_active = True
        
        await interaction.response.defer()

        while game_active and wrong_attempts < max_wrong:
            country, (image_url, valid_answers) = random.choice(list(FLAGS.items()))

            # Verify image link works before sending embed
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(image_url, timeout=3) as resp:
                        if resp.status != 200:
                            continue  # Skip broken link and roll another flag
                except Exception:
                    continue

            view = GameView(author_id=interaction.user.id, country_name=country)

            # Display score and remaining lives in the embed
            embed = discord.Embed(
                title=f"Guess the Country! | Score: {score} | Strikes: {wrong_attempts}/{max_wrong}",
                description="Type your answer in this channel within 30 seconds!\nClick **Hint** or **End Game** below anytime.",
                color=discord.Color(0x8BB96E)
            )
            embed.set_image(url=image_url)

            await interaction.followup.send(embed=embed, view=view)

            # Accept any text response from the game host to process right/wrong guesses
            def check(m: discord.Message):
                return (
                    m.channel.id == interaction.channel_id
                    and m.author.id == interaction.user.id
                )

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30.0)
                
                if view.stopped:
                    await interaction.followup.send(f"Game ended by **{interaction.user.display_name}**!\n Final Score: **{score}**.")
                    break

                guess = msg.content.strip().lower()

                if guess in valid_answers:
                    score += 1
                    await interaction.followup.send(
                        f"Bingo, you were right! It was **{country}**!"
                    )
                else:
                    wrong_attempts += 1
                    remaining = max_wrong - wrong_attempts
                    if wrong_attempts < max_wrong:
                        await interaction.followup.send(
                            f"Awh! The correct answer was **{country}**. ({remaining} {'strikes' if remaining > 1 else 'strike'} remaining)"
                        )
                    else:
                        await interaction.followup.send(
                            f"Wrong! The correct answer was **{country}**."
                        )
                        await interaction.followup.send(
                            f"# > **Game Over!**\nYou've maxed out your strikes. Final Score: **{score}**."
                        )
                        game_active = False

                await asyncio.sleep(2)

            except asyncio.TimeoutError:
                if view.stopped:
                    await interaction.followup.send(f"That's it for now! Your final score is **{score}**.")
                else:
                    wrong_attempts += 1
                    remaining = max_wrong - wrong_attempts
                    if wrong_attempts < max_wrong:
                        await interaction.followup.send(
                            f"Time's up! The correct answer was **{country}**. ({remaining} {'strikes' if remaining > 1 else 'strike'} remaining)"
                        )
                    else:
                        await interaction.followup.send(
                            f"Time's up! The correct answer was **{country}**."
                        )
                        await interaction.followup.send(
                            f"> **Game Over!**\n -#You've maxed out your strikes. Final Score: **{score}**."
                        )
                        game_active = False
                
                await asyncio.sleep(2)

async def setup(bot: commands.Bot):
    if not bot.tree.get_command("games"):
        bot.tree.add_command(games_group)
    await bot.add_cog(FlagGame(bot))
