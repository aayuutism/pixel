import asyncio
import discord
from discord import app_commands
from discord.ext import commands

PLAYER0 = "<:p0:1536795551213949089>"
PLAYER1 = "<:p1:153679556280795236>"
PLAYER2 = "<:p2:1536795603990741062>"
TICK_MARK = discord.PartialEmoji.from_str("<:check:1533886268512141393>")
TADA = "<:tada:1536797799138721812>"
TIMER = "<:timer:1536795548961480806>"
NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]


class ConnectFourBoardView(discord.ui.View):

    def __init__(self, challenger: discord.User, opponent: discord.User):
        super().__init__(timeout=300)
        self.challenger = challenger
        self.opponent = opponent
        self.turn_player = challenger
        
        self.rows, self.cols = 6, 7
        self.board = [[PLAYER0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.symbols = {challenger.id: PLAYER1, opponent.id: PLAYER2}
        
        self.update_buttons()

    def render(self) -> str:
        grid_text = "\n".join("".join(row) for row in self.board)
        return f"{grid_text}\n{''.join(NUMBERS)}"

    def update_buttons(self, disabled: bool = False):
        self.clear_items()
        for col in range(self.cols):
            is_full = self.board[0][col] != PLAYER0
            
            button = discord.ui.Button(
                label=str(col + 1),
                style=discord.ButtonStyle.primary,
                custom_id=f"c4_{col}",
                disabled=disabled or is_full,
                row=0 if col < 4 else 1,
            )
            button.callback = self.make_callback(col)
            self.add_item(button)

    def make_callback(self, col: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.turn_player.id:
                return await interaction.response.send_message(
                    f"Hold on! It's {self.turn_player.mention}'s turn right now.", ephemeral=True
                )

            current_symbol = self.symbols[self.turn_player.id]
            for r in range(self.rows - 1, -1, -1):
                if self.board[r][col] == PLAYER0:
                    self.board[r][col] = current_symbol
                    break

            if self.check_win(current_symbol):
                self.update_buttons(disabled=True)
                self.stop()
                return await interaction.response.edit_message(
                    content=f"{TADA} {self.turn_player.mention} ({current_symbol}) won Connect Four!\n\n{self.render()}",
                    view=self,
                )

            if all(cell != PLAYER0 for cell in self.board[0]):
                self.update_buttons(disabled=True)
                self.stop()
                return await interaction.response.edit_message(
                    content=f"It's a tie! Great match.\n\n{self.render()}", view=self
                )

            self.turn_player = self.opponent if self.turn_player == self.challenger else self.challenger
            self.update_buttons()
            
            next_symbol = self.symbols[self.turn_player.id]
            await interaction.response.edit_message(
                content=f"{PLAYER1} **Connect Four**: {self.challenger.mention} vs {self.opponent.mention}\n\n{self.render()}\n\n{next_symbol} {self.turn_player.mention}, your turn!",
                view=self,
            )
        return callback

    def check_win(self, piece: str) -> bool:
        for r in range(self.rows):
            for c in range(self.cols):
                if c + 3 < self.cols and all(self.board[r][c+i] == piece for i in range(4)): return True
                if r + 3 < self.rows and all(self.board[r+i][c] == piece for i in range(4)): return True
                if r + 3 < self.rows and c + 3 < self.cols and all(self.board[r+i][c+i] == piece for i in range(4)): return True
                if r - 3 >= 0 and c + 3 < self.cols and all(self.board[r-i][c+i] == piece for i in range(4)): return True
        return False

    async def on_timeout(self):
        self.update_buttons(disabled=True)


class ConnectFourInviteView(discord.ui.View):

    def __init__(self, challenger: discord.User, opponent: discord.User | None):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.opponent = opponent
        self.accepted = False

    @discord.ui.button(emoji=TICK_MARK, style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.challenger.id:
            return await interaction.response.send_message("You can't play against yourself!", ephemeral=True)
        
        if self.opponent and interaction.user.id != self.opponent.id:
            return await interaction.response.send_message(f"Only {self.opponent.mention} can accept this invite.", ephemeral=True)

        self.accepted = True
        if not self.opponent:
            self.opponent = interaction.user
            
        await interaction.response.defer()
        self.stop()


class ConnectFourCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="games-connectfour", description="Play Connect Four with a friend")
    @app_commands.describe(player="The user you want to play against (leave blank for anyone)")
    async def connectfour(self, interaction: discord.Interaction, player: discord.User | None = None):
        await interaction.response.defer()

        if player and player.id == interaction.user.id:
            return await interaction.followup.send("You can't play against yourself, silly!", ephemeral=True)
        if player and player.bot:
            return await interaction.followup.send("Oi, pick a real person to play with!", ephemeral=True)

        invite_view = ConnectFourInviteView(interaction.user, player)
        target_mention = player.mention if player else "Anyone"
        
        msg = await interaction.followup.send(
            content=f"{target_mention} > Join {interaction.user.mention} in Connect Four!", view=invite_view
        )

        if await invite_view.wait() or not invite_view.accepted:
            invite_view.accept.disabled = True
            return await interaction.followup.edit_message(
                message_id=msg.id, content=f"{TIMER} **The game invitation has expired.**", view=invite_view
            )

        board_view = ConnectFourBoardView(interaction.user, invite_view.opponent)
        await interaction.followup.edit_message(
            message_id=msg.id,
            content=f"{PLAYER1} **Connect Four**: {interaction.user.mention} vs {invite_view.opponent.mention}\n\n{board_view.render()}\n\n{PLAYER1} {interaction.user.mention}, it's your turn!",
            view=board_view,
        )

        if await board_view.wait():
            board_view.update_buttons(disabled=True)
            await interaction.followup.edit_message(
                message_id=msg.id, content=f"{TIMER} The game timed out due to inactivity!\n\n{board_view.render()}", view=board_view
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ConnectFourCog(bot))
