import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

COOKIE = "<:cookie:1545403826369208402>"
TIMER = "<:timer:1536795548961480806>"
TADA = "<:tada:1536797799138721812>"
TICK = "<:i_check:1539237416806645811>"


class CookieGameView(discord.ui.View):

    def __init__(self, player1: discord.User, player2: discord.User):
        super().__init__(timeout=15.0)
        self.player1 = player1
        self.player2 = player2
        self.winner: discord.User | None = None

    @discord.ui.button(emoji=COOKIE, style=discord.ButtonStyle.success)
    async def cookie_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in (self.player1.id, self.player2.id):
            return await interaction.response.send_message("This isn't your cookie game!", ephemeral=True)

        self.winner = interaction.user
        for child in self.children:
            child.disabled = True
        self.stop()
        
        embed = discord.Embed(
            title="Cookie Clicker",
            description=f"{TADA} {interaction.user.mention} clicked the cookie first! {COOKIE}",
            color=discord.Color(0x131416)
        )
        await interaction.response.edit_message(embed=embed, view=self)


class CookieInviteView(discord.ui.View):

    def __init__(self, challenger: discord.User, opponent: discord.User):
        super().__init__(timeout=30)
        self.challenger = challenger
        self.opponent = opponent
        self.accepted = False

    @discord.ui.button(emoji=TICK, style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.challenger.id:
            return await interaction.response.send_message("You can't play against yourself!", ephemeral=True)
        
        if interaction.user.id != self.opponent.id:
            return await interaction.response.send_message(f"This invite is specifically for {self.opponent.mention}!", ephemeral=True)

        self.accepted = True
        for child in self.children:
            child.disabled = True
        await interaction.response.defer()
        self.stop()


class CookieCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="games-cookie", description="Test your reflexes and click the cookie first against a friend!")
    @app_commands.describe(player="Pick who you wanna play against!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def cookie(self, interaction: discord.Interaction, player: discord.User):
        if player.id == interaction.user.id:
            return await interaction.response.send_message("You really wanna play against yourself?", ephemeral=True)
        if player.bot:
            return await interaction.response.send_message("Oi, pick a real person to play with.", ephemeral=True)

        invite_view = CookieInviteView(interaction.user, player)
        invite_embed = discord.Embed(
            title="Cookie Clicker Invitation",
            description=f"{player.mention}, you have been challenged to a Cookie Clicker duel by {interaction.user.mention}!\n\nClick the button to accept {COOKIE}",
            color=discord.Color(0x131416)
        )
        
        await interaction.response.send_message(embed=invite_embed, view=invite_view)
        msg = await interaction.original_response()

        if await invite_view.wait() or not invite_view.accepted:
            for child in invite_view.children:
                child.disabled = True
            timeout_embed = discord.Embed(
                title="Cookie Clicker Invitation",
                description=f"{TIMER} **The cookie invitation timed out.**",
                color=discord.Color(0x131416)
            )
            return await interaction.edit_original_response(embed=timeout_embed, view=invite_view)

        start_embed = discord.Embed(
            title="Cookie Clicker",
            description=f"Get ready, {interaction.user.mention} vs {player.mention}... The cookie is coming! {COOKIE}",
            color=discord.Color(0x131416)
        )
        await interaction.edit_original_response(embed=start_embed, view=None)

        delay = random.randint(2, 5)
        for countdown in range(delay, 0, -1):
            await asyncio.sleep(1)
            countdown_embed = discord.Embed(
                title="Cookie Clicker",
                description=f"Get ready... Click in **{countdown}** {COOKIE}",
                color=discord.Color(0x131416)
            )
            await interaction.edit_original_response(embed=countdown_embed)

        view = CookieGameView(interaction.user, player)
        game_embed = discord.Embed(
            title="Cookie Clicker",
            description=f"**Click the cookie!** {COOKIE}",
            color=discord.Color(0x131416)
        )
        await interaction.edit_original_response(embed=game_embed, view=view)

        await view.wait()

        if view.winner is None:
            for child in view.children:
                child.disabled = True
            timeout_embed = discord.Embed(
                title="Cookie Clicker",
                description=f"{TIMER} Nobody clicked the cookie in time!",
                color=discord.Color(0x131416)
            )
            await interaction.edit_original_response(embed=timeout_embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(CookieCog(bot))
