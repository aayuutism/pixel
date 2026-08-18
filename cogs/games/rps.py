import discord
from discord import app_commands
from discord.ext import commands
from groups import games_group  # <--- IMPORT SHARED GROUP FROM ROOT

EMOJI_MAP = {
    "rock": "👊",
    "paper": "✋",
    "scissors": "✌️",
}


# --- RPS GAME VIEW (STAGE 2) ---
class RPSGameView(discord.ui.View):

    def __init__(self, challenger: discord.User, opponent: discord.User):
        super().__init__(timeout=120)  # 2 minutes
        self.challenger = challenger
        self.opponent = opponent
        self.moves: dict[int, str] = {}
        self.update_buttons()

    def update_buttons(self, disabled: bool = False):
        self.clear_items()
        for move_key, emoji in EMOJI_MAP.items():
            button = discord.ui.Button(
                emoji=emoji,
                style=discord.ButtonStyle.secondary,
                custom_id=f"rps_{move_key}",
                disabled=disabled,
            )
            button.callback = self.make_move_callback(move_key)
            self.add_item(button)

    def make_move_callback(self, move_choice: str):

        async def move_callback(interaction: discord.Interaction):
            user_id = interaction.user.id

            if user_id not in (self.challenger.id, self.opponent.id):
                return await interaction.response.send_message(
                    "You are not part of this game!", ephemeral=True
                )

            if user_id in self.moves:
                return await interaction.response.send_message(
                    "You have already made your move!", ephemeral=True
                )

            self.moves[user_id] = move_choice

            # First move locked
            if len(self.moves) == 1:
                waiting_for = (
                    self.opponent
                    if user_id == self.challenger.id
                    else self.challenger
                )
                first_chooser_name = interaction.user.name
                waiting_name = waiting_for.name

                await interaction.response.edit_message(
                    content=(
                        f"{waiting_for.mention}\n"
                        f"> {first_chooser_name} locked their choice\n"
                        f"> {waiting_name} is choosing..."
                    ),
                    view=self,
                )

            # Both moves locked -> Determine Winner
            elif len(self.moves) == 2:
                self.update_buttons(disabled=True)
                self.stop()

                move1 = self.moves[self.challenger.id]
                move2 = self.moves[self.opponent.id]

                if move1 == move2:
                    result_text = (
                        f"> ### It's a tie!\n> Both chose {EMOJI_MAP[move1]}"
                    )
                elif (
                    (move1 == "rock" and move2 == "scissors")
                    or (move1 == "paper" and move2 == "rock")
                    or (move1 == "scissors" and move2 == "paper")
                ):
                    result_text = (
                        f"> {self.challenger.mention} **won with** {EMOJI_MAP[move1]}\n\n"
                        f"> {self.challenger.name} chose {EMOJI_MAP[move1]} & "
                        f"{self.opponent.name} chose {EMOJI_MAP[move2]}"
                    )
                else:
                    result_text = (
                        f"> {self.opponent.mention} **won with** {EMOJI_MAP[move2]}\n\n"
                        f"> {self.challenger.name} chose {EMOJI_MAP[move1]} & "
                        f"{self.opponent.name} chose {EMOJI_MAP[move2]}"
                    )

                await interaction.response.edit_message(
                    content=result_text, view=self
                )

        return move_callback


# --- INVITATION VIEW (STAGE 1) ---
class RPSInviteView(discord.ui.View):

    def __init__(
        self, challenger: discord.User, opponent: discord.User | None
    ):
        super().__init__(timeout=60)  # 60 seconds
        self.challenger = challenger
        self.opponent = opponent
        self.game_accepted = False

    @discord.ui.button(emoji="✅", style=discord.ButtonStyle.success)
    async def accept(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.challenger.id:
            return await interaction.response.send_message(
                "You can't accept your own invitation!", ephemeral=True
            )

        if self.opponent and interaction.user.id != self.opponent.id:
            return await interaction.response.send_message(
                f"Only {self.opponent.mention} can accept this invitation!",
                ephemeral=True,
            )

        self.game_accepted = True
        if not self.opponent:
            self.opponent = interaction.user

        await interaction.response.defer()
        self.stop()


# --- MAIN COG ---
class RPSCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @games_group.command(
        name="rps", description="Play Rock-Paper-Scissors with a friend"
    )
    @app_commands.describe(
        player="The user you want to play against (optional)"
    )
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def rps(
        self,
        interaction: discord.Interaction,
        player: discord.User | None = None,
    ):
        challenger = interaction.user
        opponent = player

        if opponent and opponent.id == challenger.id:
            return await interaction.response.send_message(
                "You can't play Rock-Paper-Scissors against yourself!",
                ephemeral=True,
            )

        if opponent and opponent.bot:
            return await interaction.response.send_message(
                "You can't challenge bots!", ephemeral=True
            )

        invite_view = RPSInviteView(challenger, opponent)
        invite_text = (
            f"{opponent.mention} > Click the button to play Rock-Paper-Scissors with {challenger.mention}!"
            if opponent
            else f"> Click the button to play Rock-Paper-Scissors with {challenger.mention}!"
        )

        await interaction.response.send_message(
            content=invite_text, view=invite_view
        )
        msg = await interaction.original_response()

        # Wait for invitation response or timeout
        timed_out = await invite_view.wait()
        if timed_out or not invite_view.game_accepted:
            invite_view.accept.disabled = True
            expired_text = (
                f"⏰ **The game invitation has expired.**\n\n{opponent.mention} > Click the button to play Rock-Paper-Scissors with {challenger.mention}!"
                if opponent
                else f"⏰ **The game invitation has expired.**\n\n> Click the button to play Rock-Paper-Scissors with {challenger.mention}!"
            )
            return await interaction.followup.edit_message(
                message_id=msg.id, content=expired_text, view=invite_view
            )

        # Transition to game board in command scope
        game_view = RPSGameView(challenger, invite_view.opponent)
        await interaction.followup.edit_message(
            message_id=msg.id,
            content=(
                f"{challenger.mention} {invite_view.opponent.mention}\n"
                f"> ### Any of you can go first\n"
                f"> Click a button to make your move"
            ),
            view=game_view,
        )

        game_timed_out = await game_view.wait()
        if game_timed_out and len(game_view.moves) < 2:
            game_view.update_buttons(disabled=True)
            await interaction.followup.edit_message(
                message_id=msg.id,
                content="⏰ Rock-Paper-Scissors game timed out due to inactivity!",
                view=game_view,
            )


async def setup(bot: commands.Bot):
    if not bot.get_cog("RPSCog"):
        await bot.add_cog(RPSCog(bot))
