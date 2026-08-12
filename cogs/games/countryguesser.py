from __future__ import annotations

import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

# Import the flag dictionary from flags.py
from .flags import FLAGS


class ChatFlagGame:
    def __init__(self, bot: commands.Bot, user: discord.User, channel: discord.TextChannel):
        self.bot = bot
        self.user = user
        self.channel = channel
        self.score = 0
        self.total = 0
        self.is_active = True

    def create_flag_embed(self, flag_url: str) -> discord.Embed:
        embed = discord.Embed(
            title="Guess the country!",
            description="Which country does this flag belong to?",
            color=discord.Color.from_rgb(47, 49, 54),
        )
        embed.set_thumbnail(url=flag_url)
        embed.set_footer(text="type your answer down below!")
        return embed

    async def start(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Starting flag guesser! Get ready...", ephemeral=True)

        while self.is_active:
            country_name, (flag_url, valid_answers) = random.choice(list(FLAGS.items()))
            embed = self.create_flag_embed(flag_url)

            await self.channel.send(embed=embed)

            def check(msg: discord.Message) -> bool:
                return (
                    msg.channel == self.channel
                    and msg.author == self.user
                    and not msg.author.bot
                )

            try:
                # Waits 30 seconds for the user to type their answer in chat
                guess_msg = await self.bot.wait_for("message", check=check, timeout=30.0)
                user_guess = guess_msg.content.strip().lower()

                if user_guess in valid_answers:
                    self.score += 1
                    self.total += 1
                    await self.channel.send(
                        f"Congrats, you got it! **{self.score}/{self.total}** Moving onto the next one!"
                    )
                    await asyncio.sleep(1.5)
                else:
                    self.total += 1
                    await self.channel.send(
                        f"Aww, incorrect! The correct answer was **{country_name}**.\n"
                        f"Final Streak: **{self.score}/{self.total}**"
                    )
                    self.is_active = False

            except asyncio.TimeoutError:
                await self.channel.send(
                    f"Time's up! The country was **{country_name}**.\n"
                    f"Final Streak: **{self.score}/{self.total}**"
                )
                self.is_active = False


class CountryGuesserCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="guess", description="Play chat-based flag guesser!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def guess(self, interaction: discord.Interaction):
        game = ChatFlagGame(self.bot, interaction.user, interaction.channel)
        await game.start(interaction)


async def setup(bot: commands.Bot):
    if not bot.get_cog("CountryGuesserCog"):
        await bot.add_cog(CountryGuesserCog(bot))
