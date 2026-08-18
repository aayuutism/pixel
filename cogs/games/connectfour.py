import asyncio
import discord
from discord import app_commands
from discord.ext import commands

games_group = app_commands.Group(name="games", description="Play various mini-games!")

# --- EMOJIS ---
PLAYER0 = "<:p0:1536795551213949089>"
PLAYER1 = "<:p1:153679556280795236>"
PLAYER2 = "<:p2:1536795603990741062>"
TICK_MARK = discord.PartialEmoji.from_str("<:check:1533886268512141393>")
TADA = "<:tada:1536797799138721812>"
TIMER = "<:timer:1536795548961480806>"

# Default numeric emojis
NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]


# --- BOARD VIEW (STAGE 2) ---
class ConnectFourBoardView(discord.ui.View):

    def __init__(self, challenger: discord.User, opponent: discord.User):
        super().__init__(timeout=300)  # 5 minutes
        self.challenger = challenger
        self.opponent = opponent
        self.turn_player = challenger

        self.ROWS = 6
        self.COLS = 7
        self.board = [
            [PLAYER0 for _ in range(self.COLS)] for _ in range(self.ROWS)
        ]
        self.player_symbols = {
            challenger.id: PLAYER1,
            opponent.id: PLAYER2,
        }

        self.update_buttons()

    def render_board(self) -> str:
        board_text = "\n".join("".join(row) for row in self.board)
        board_text += "\n" + "".join(NUMBERS)
        return board_text

    def update_buttons(self, disabled: bool = False):
        self.clear_items()
        for col in range(self.COLS):
            col_full = self.board[0][col] != PLAYER0
            button = discord.ui.Button(
                label=str(col + 1),
                style=discord.ButtonStyle.primary,
                custom_id=f"c4_col_{col}",
                disabled=disabled or col_full,
                row=0 if col < 4 else 1,
            )
            button.callback = self.make_column_callback(col)
            self.add_item(button)

    def make_column_callback(self, col_index: int):

        async def column_callback(interaction: discord.Interaction):
            if interaction.user.id != self.turn_player.id:
                return await interaction.response.send_message(
                    f"It's {self.turn_player.mention}'s turn right now",
                    ephemeral=True,
                )

            current_symbol = self.player_symbols[self.turn_player.id]

            # Drop piece
            for r in range(self.ROWS - 1, -1, -1):
                if self.board[r][col_index] == PLAYER0:
                    self.board[r][col_index] = current_symbol
                    break

            # Check Win
            if self.check_win(current_symbol):
                self.update_buttons(disabled=True)
                self.stop()
                return await interaction.response.edit_message(
                    content=f"{TADA} {self.turn_player.mention} ({current_symbol}) won Connect Four!\n\n{self.render_board()}",
                    view=self,
                )

            # Check Tie
            if self.is_board_full():
                self.update_buttons(disabled=True)
                self.stop()
                return await interaction.response.edit_message(
                    content=f"This game ended in a tie!\n\n{self.render_board()}",
                    view=self,
                )

            # Switch turns
            self.turn_player = (
                self.opponent
                if self.turn_player.id == self.challenger.id
                else self.challenger
            )
            next_symbol = self.player_symbols[self.turn_player.id]

            self.update_buttons()
            await interaction.response.edit_message(
                content=f"{PLAYER1} **Connect Four**: {self.challenger.mention} ({PLAYER1}) vs {self.opponent.mention} ({PLAYER2})\n\n{self.render_board()}\n\n{next_symbol} {self.turn_player.mention}, your turn!",
                view=self,
            )

        return column_callback

    def check_win(self, piece: str) -> bool:
        # Horizontal
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                if (
                    self.board[r][c] == piece
                    and self.board[r][c + 1] == piece
                    and self.board[r][c + 2] == piece
                    and self.board[r][c + 3] == piece
                ):
                    return True
        # Vertical
        for r in range(self.ROWS - 3):
            for c in range(self.COLS):
                if (
                    self.board[r][c] == piece
                    and self.board[r + 1][c] == piece
                    and self.board[r + 2][c] == piece
                    and self.board[r + 3][c] == piece
                ):
                    return True
        # Diagonal (Down-Right)
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                if (
                    self.board[r][c] == piece
                    and self.board[r + 1][c + 1] == piece
                    and self.board[r + 2][c + 2] == piece
                    and self.board[r + 3][c + 3] == piece
                ):
                    return True
        # Diagonal (Up-Right)
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                if (
                    self.board[r][c] == piece
                    and self.board[r - 1][c + 1] == piece
                    and self.board[r - 2][c + 2] == piece
                    and self.board[r - 3][c + 3] == piece
                ):
                    return True
        return False

    def is_board_full(self) -> bool:
        return all(cell != PLAYER0 for cell in self.board[0])

    async def on_timeout(self):
        self.update_buttons(disabled=True)


# --- INVITATION VIEW (STAGE 1) ---
class ConnectFourInviteView(discord.ui.View):

    def __init__(
        self, challenger: discord.User, opponent: discord.User | None
    ):
        super().__init__(timeout=60)  # 60 seconds
        self.challenger = challenger
        self.opponent = opponent
        self.game_accepted = False

    @discord.ui.button(emoji=TICK_MARK, style=discord.ButtonStyle.success)
    async def accept(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.challenger.id:
            return await interaction.response.send_message(
                "You can't accept your own invitation!", ephemeral=True
            )

        if self.opponent and interaction.user.id != self.opponent.id:
            return await interaction.response.send_message(
                f"Only {self.opponent.mention} can accept this invitation",
                ephemeral=True,
            )

        self.game_accepted = True
        if not self.opponent:
            self.opponent = interaction.user

        await interaction.response.defer()
        self.stop()


# --- MAIN COG ---
class ConnectFourCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @games_group.command(
        name="connectfour", description="Play Connect Four with a friend"
    )
    @app_commands.describe(player="The user you want to play against (optional)")
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def connectfour(
        self,
        interaction: discord.Interaction,
        player: discord.User | None = None,
    ):
        await interaction.response.defer()

        challenger = interaction.user
        opponent = player

        if opponent and opponent.id == challenger.id:
            return await interaction.followup.send(
                "You can't play against yourself, silly!"
            )

        if opponent and opponent.bot:
            return await interaction.followup.send(
                "Oi, pick a real person to play with!"
            )

        invite_view = ConnectFourInviteView(challenger, opponent)
        invite_text = (
            f"{opponent.mention} > Join {challenger.mention} in Connect Four!"
            if opponent
            else f"> Join {challenger.mention} in Connect Four!"
        )

        msg = await interaction.followup.send(
            content=invite_text, view=invite_view
        )

        # Wait for invitation response or timeout
        timed_out = await invite_view.wait()
        if timed_out or not invite_view.game_accepted:
            invite_view.accept.disabled = True
            expired_text = (
                f"{TIMER} **The game invitation has expired.**\n\n{opponent.mention} > Click the button to play Connect Four with {challenger.mention}!"
                if opponent
                else f"{TIMER} **The game invitation has expired.**\n\n> Click the button to play Connect Four with {challenger.mention}!"
            )
            return await interaction.followup.edit_message(
                message_id=msg.id, content=expired_text, view=invite_view
            )

        # Start game flow
        board_view = ConnectFourBoardView(challenger, invite_view.opponent)
        await interaction.followup.edit_message(
            message_id=msg.id,
            content=f"{PLAYER1} **Connect Four**: {challenger.mention} ({PLAYER1}) vs {invite_view.opponent.mention} ({PLAYER2})\n\n{board_view.render_board()}\n\n{PLAYER1} {challenger.mention}, it's your turn!",
            view=board_view,
        )

        game_timed_out = await board_view.wait()
        if game_timed_out:
            board_view.update_buttons(disabled=True)
            await interaction.followup.edit_message(
                message_id=msg.id,
                content=f"{TIMER} The game timed out due to inactivity!\n\n{board_view.render_board()}",
                view=board_view,
            )


async def setup(bot: commands.Bot):
    if not bot.tree.get_command("games"):
        bot.tree.add_command(games_group)
    await bot.add_cog(ConnectFourCog(bot))
