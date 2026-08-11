import discord
from discord import app_commands
from discord.ext import commands

# --- CUSTOM EMOJIS & CONSTANTS ---
P1= "<:ttt_x:1536802209189339146>"
P2= "<:ttt_o:1536802206202724526>"
TICK_MARK = 1533886268512141393 
TADA = "<:tada:1536797799138721812>"
TIMER = "<:timer:1536795548961480806>"


# --- BOARD BUTTON ---
class TicTacToeButton(discord.ui.Button):

    def __init__(self, x: int, y: int):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label="\u200b",
            row=y,
        )
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeBoardView = self.view  # type: ignore

        if interaction.user.id != view.turn_player.id:
            return await interaction.response.send_message(
                f"It's {view.turn_player.mention}'s turn right now",
                ephemeral=True,
            )

        index = self.y * 3 + self.x
        if view.board[index] is not None:
            return await interaction.response.send_message(
                "That spot is already taken!", ephemeral=True
            )

        symbol = "X" if view.turn_player.id == view.challenger.id else "O"
        view.board[index] = symbol

        if symbol == "X":
            self.label = "X"
            self.style = discord.ButtonStyle.danger
        else:
            self.label = "O"
            self.style = discord.ButtonStyle.success

        winner = view.check_winner()

        if winner:
            view.disable_all_buttons()
            view.stop()

            if winner == "TIE":
                final_status = "The game has ended in a tie!"
            else:
                final_status = f"{TADA} {view.turn_player.mention} ({symbol}) won the game!"

            return await interaction.response.edit_message(
                content=f" **Tic-Tac-Toe Game Over!**\n\n{final_status}",
                view=view,
            )

        # Switch turns
        view.turn_player = (
            view.opponent
            if view.turn_player.id == view.challenger.id
            else view.challenger
        )
        next_symbol = (
            CROSS if view.turn_player.id == view.challenger.id else ZERO
        )

        await interaction.response.edit_message(
            content=(
                f"**{view.challenger.display_name}** ({CROSS}) vs **{view.opponent.display_name}** ({ZERO})\n\n"
                f"{next_symbol} {view.turn_player.mention}, your turn!"
            ),
            view=view,
        )


# --- TIC-TAC-TOE GAME BOARD VIEW (STAGE 2) ---
class TicTacToeBoardView(discord.ui.View):

    def __init__(self, challenger: discord.User, opponent: discord.User):
        super().__init__(timeout=300)  # 5 minutes
        self.challenger = challenger
        self.opponent = opponent
        self.turn_player = challenger
        self.board = [None] * 9

        # Build 3x3 grid
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))

    def disable_all_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    def check_winner(self) -> str | None:
        lines = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],  # Rows
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],  # Columns
            [0, 4, 8],
            [2, 4, 6],  # Diagonals
        ]
        for line in lines:
            a, b, c = line
            if (
                self.board[a]
                and self.board[a] == self.board[b] == self.board[c]
            ):
                return self.board[a]

        if all(cell is not None for cell in self.board):
            return "TIE"

        return None


# --- INVITATION VIEW (STAGE 1) ---
class TicTacToeInviteView(discord.ui.View):

    def __init__(
        self, challenger: discord.User, opponent: discord.User | None
    ):
        super().__init__(timeout=60)  # 60 seconds
        self.challenger = challenger
        self.opponent = opponent
        self.game_accepted = False

    @discord.ui.button(
        emoji=discord.PartialEmoji(name="tick", id=TICK_MARK),
        style=discord.ButtonStyle.success,
    )
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

        self.stop()

        board_view = TicTacToeBoardView(self.challenger, self.opponent)
        await interaction.response.edit_message(
            content=(
                f" **Tic-Tac-Toe**: {self.challenger.mention} ({CROSS}) vs {self.opponent.mention} ({ZERO})\n\n"
                f"{CROSS} {self.challenger.mention}, it's your turn!"
            ),
            view=board_view,
        )

        # Wait for the game to complete or time out
        timed_out = await board_view.wait()
        if timed_out:
            board_view.disable_all_buttons()
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content=f"{TIMER} Tic-Tac-Toe game timed out due to inactivity!",
                view=board_view,
            )


# --- MAIN COG ---
class TicTacToeCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="tictactoe", description="Play TicTacToe with a friend"
    )
    @app_commands.describe(player="The user you want to play against (optional)")
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def tictactoe(
        self,
        interaction: discord.Interaction,
        player: discord.User | None = None,
    ):
        challenger = interaction.user
        opponent = player

        if opponent and opponent.id == challenger.id:
            return await interaction.response.send_message(
                "You can't play Tic-Tac-Toe against yourself!", ephemeral=True
            )

        if opponent and opponent.bot:
            return await interaction.response.send_message(
                "You can't challenge bots to Tic-Tac-Toe!", ephemeral=True
            )

        invite_view = TicTacToeInviteView(challenger, opponent)
        invite_text = (
            f"{opponent.mention} > Click the button to play Tic-Tac-Toe with {challenger.mention}!"
            if opponent
            else f"> Click the button to play Tic-Tac-Toe with {challenger.mention}!"
        )

        await interaction.response.send_message(
            content=invite_text, view=invite_view
        )
        msg = await interaction.original_response()

        # Wait for invitation response or timeout
        timed_out = await invite_view.wait()
        if timed_out and not invite_view.game_accepted:
            invite_view.accept.disabled = True
            expired_text = (
                f"{TIMER} **The game invitation has expired.**\n\n{opponent.mention} > Click the button to play Tic-Tac-Toe with {challenger.mention}!"
                if opponent
                else f"{TIMER} **The game invitation has expired.**\n\n> Click the button to play Tic-Tac-Toe with {challenger.mention}!"
            )
            await interaction.followup.edit_message(
                message_id=msg.id, content=expired_text, view=invite_view
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(TicTacToeCog(bot))
