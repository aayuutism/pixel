from __future__ import annotations

import os
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

# Import your existing core Wordle logic class
from ..wordle import Wordle


class WordInput(discord.ui.Modal, title="Word Input"):
    word = discord.ui.TextInput(
        label="Input your guess",
        style=discord.TextStyle.short,
        required=True,
        min_length=5,
        max_length=5,
    )

    def __init__(self, view: WordleView) -> None:
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction) -> None:
        content = self.word.value.lower()
        game = self.view.game

        if content not in game._valid_words:
            return await interaction.response.send_message(
                "that's not a valid word, try again!", ephemeral=True
            )

        won = game.parse_guess(content)
        buf = await game.render_image()

        embed = discord.Embed(title="Wordle!", color=self.view.game.embed_color)
        embed.set_image(url="attachment://wordle.png")
        file = discord.File(buf, "wordle.png")

        loss = len(game.guesses) >= 6

        if won:
            await interaction.channel.send(
                f"gg {interaction.user.mention}! you got it right 🎉"
            )
        elif loss:
            await interaction.channel.send(
                f"game over! the word was **{game.word}**."
            )

        if won or loss:
            self.view.disable_all_items()
            self.view.stop()

        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self.view
        )


class WordInputButton(discord.ui.Button["WordleView"]):
    def __init__(self, *, cancel_button: bool = False):
        super().__init__(
            label="Cancel" if cancel_button else "Make a guess!",
            style=discord.ButtonStyle.red if cancel_button else discord.ButtonStyle.blurple,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game
        if interaction.user != game.player:
            return await interaction.response.send_message(
                "this isn't your game!", ephemeral=True
            )

        if self.label == "Cancel":
            await interaction.response.send_message(
                f"game cancelled. the word was **{game.word}**."
            )
            await interaction.message.delete()
            return self.view.stop()
        else:
            return await interaction.response.send_modal(WordInput(self.view))


class WordleView(discord.ui.View):
    def __init__(self, game: BetaWordle, *, timeout: Optional[float] = 180.0):
        super().__init__(timeout=timeout)
        self.game = game
        self.add_item(WordInputButton())
        self.add_item(WordInputButton(cancel_button=True))

    def disable_all_items(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


class BetaWordle(Wordle):
    player: discord.User
    embed_color: discord.Color

    async def start(
        self,
        interaction: discord.Interaction,
        *,
        timeout: Optional[float] = 180.0,
    ) -> None:
        self.embed_color = discord.Color.random()
        self.player = interaction.user

        buf = await self.render_image()
        embed = discord.Embed(title="Wordle!", color=self.embed_color)
        embed.set_image(url="attachment://wordle.png")

        self.view = WordleView(self, timeout=timeout)
        
        await interaction.response.send_message(
            embed=embed,
            file=discord.File(buf, "wordle.png"),
            view=self.view,
        )


class WordleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="wordle", description="Play a game of Wordle!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def wordle(self, interaction: discord.Interaction):
        game = BetaWordle()
        await game.start(interaction)


async def setup(bot: commands.Bot):
    if not bot.get_cog("WordleCog"):
        await bot.add_cog(WordleCog(bot))
