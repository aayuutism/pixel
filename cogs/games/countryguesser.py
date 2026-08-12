from __future__ import annotations

import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

# Import your custom flags dictionary from cogs/games/flags.py
from .flags import FLAGS


class CountryGuesser:
    def __init__(
        self,
        bot: commands.Bot,
        user: discord.User | discord.Member,
        channel: discord.TextChannel | discord.DMChannel | discord.GroupChannel | discord.Thread,
    ):
        self.bot = bot
        self.user = user
        self.channel = channel
        self.score = 0
        self.total = 0
        self.is_active = True
        self.last_country: str | None = None

    def build_embed(self, flag_url: str) -> discord.Embed:
        embed = discord.Embed(
            title="Guess the country!",
            description="Which country does this flag belong to?",
            color=discord.Color.from_rgb(47, 49, 54),
        )
        embed.set_image(url=flag_url)
        embed.set_footer(text="type your answer down below!")
        return embed

    async def run(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Starting flag guesser! Get ready...", ephemeral=True)

        # Main game loop — keeps running until self.is_active becomes False
        while self.is_active:
            # Pick a country that isn't the same as the previous round
            available_countries = [c for c in FLAGS.keys() if c != self.last_country]
            country_name = random.choice(available_countries)
            self.last_country = country_name

            flag_url, accepted_answers = FLAGS[country_name]
            embed = self.build_embed(flag_url)

            await self.channel.send(embed=embed)

            def check(msg: discord.Message) -> bool:
                return (
                    msg.channel == self.channel
                    and msg.author == self.user
                    and not msg.author.bot
                )

            try:
                # Wait 30 seconds for player input
                guess_msg = await self.bot.wait_for("message", check=check, timeout=30.0)
                user_guess = guess_msg.content.strip().lower()

                # Allow player to gracefully exit
                if user_guess in ["quit", "stop", "exit"]:
                    await self.channel.send(f"Game ended! Final Score: **{self.score}/{self.total}**")
                    self.is_active = False
                    break

                if user_guess in accepted_answers:
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
                    self.is_active = False  # Ends the while loop on a wrong guess

            except asyncio.TimeoutError:
                await self.channel.send(
                    f"Time's up! The country was **{country_name}**.\n"
                    f"Final Streak: **{self.score}/{self.total}**"
                )
                self.is_active = False  # Ends the while loop on timeout


class CountryGuesserCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="countryguesser",
        description="Play infinite flag guesser until you get one wrong!",
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def countryguesser(self, interaction: discord.Interaction):
        if not interaction.channel or not isinstance(
            interaction.channel,
            (discord.TextChannel, discord.DMChannel, discord.GroupChannel, discord.Thread),
        ):
            await interaction.response.send_message(
                "Unable to start the game in this channel context.", ephemeral=True
            )
            return

        game = CountryGuesser(self.bot, interaction.user, interaction.channel)
        await game.run(interaction)


async def setup(bot: commands.Bot):
    if not bot.get_cog("CountryGuesserCog"):
        await bot.add_cog(CountryGuesserCog(bot))
