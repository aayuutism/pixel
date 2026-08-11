from __future__ import annotations

import os
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

# Import your existing core Chess logic class
from ..chess_game import Chess


class ChessInput(discord.ui.Modal, title="Make your move"):
    def __init__(self, view: ChessView) -> None:
        super().__init__()
        self.view = view

        self.move_from = discord.ui.TextInput(
            label="From coordinate (e.g. e2)",
            style=discord.TextStyle.short,
            required=True,
            min_length=2,
            max_length=2,
        )

        self.move_to = discord.ui.TextInput(
            label="To coordinate (e.g. e4)",
            style=discord.TextStyle.short,
            required=True,
            min_length=2,
            max_length=2,
        )

        self.add_item(self.move_from)
        self.add_item(self.move_to)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        game = self.view.game
        from_coord = self.move_from.value.strip().lower()
        to_coord = self.move_to.value.strip().lower()

        uci = from_coord + to_coord

        try:
            is_valid_uci = game.board.parse_uci(uci)
        except ValueError:
            is_valid_uci = False

        if not is_valid_uci:
            return await interaction.response.send_message(
                f"invalid move: `{from_coord} -> {to_coord}`. try again!",
                ephemeral=True,
            )

        await game.place_move(uci)

        if game.board.is_game_over():
            self.view.disable_all()
            embed = await game.fetch_results()
            self.view.stop()
        else:
            embed = await game.make_embed()

        await interaction.response.edit_message(embed=embed, view=self.view)


class ChessButton(discord.ui.Button["ChessView"]):
    def __init__(self, *, cancel_button: bool = False):
        super().__init__(
            label="Cancel" if cancel_button else "Make your move!",
            style=discord.ButtonStyle.red if cancel_button else discord.ButtonStyle.blurple,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        game = self.view.game
        if interaction.user not in (game.black, game.white):
            return await interaction.response.send_message(
                "you aren't part of this game!", ephemeral=True
            )

        if self.label == "Cancel":
            self.view.disable_all()
            await interaction.message.edit(view=self.view)
            await interaction.response.send_message("game cancelled.")
            return self.view.stop()
        else:
            if interaction.user != game.turn:
                return await interaction.response.send_message(
                    "it's not your turn yet!", ephemeral=True
                )
            return await interaction.response.send_modal(ChessInput(self.view))


class ChessView(discord.ui.View):
    def __init__(self, game: BetaChess, *, timeout: Optional[float] = 300.0) -> None:
        super().__init__(timeout=timeout)
        self.game = game

        self.add_item(ChessButton())
        self.add_item(ChessButton(cancel_button=True))

    def disable_all() -> None:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


class BetaChess(Chess):
    async def start(
        self,
        interaction: discord.Interaction,
        opponent: discord.User,
        *,
        timeout: Optional[float] = 300.0,
    ) -> None:
        self.white = interaction.user
        self.black = opponent
        self.turn = self.white
        self.embed_color = discord.Color.random()

        embed = await self.make_embed()
        self.view = ChessView(self, timeout=timeout)

        await interaction.response.send_message(embed=embed, view=self.view)


class ChessCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="chess", description="Challenge someone to a game of chess!")
    @app_commands.describe(opponent="Who do you want to play against?")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def chess(self, interaction: discord.Interaction, opponent: discord.User):
        if opponent == interaction.user:
            return await interaction.response.send_message(
                "you can't play against yourself!", ephemeral=True
            )
        if opponent.bot:
            return await interaction.response.send_message(
                "you can't play chess against bots!", ephemeral=True
            )

        game = BetaChess()
        await game.start(interaction, opponent)


async def setup(bot: commands.Bot):
    if not bot.get_cog("ChessCog"):
        await bot.add_cog(ChessCog(bot))
