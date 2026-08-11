import asyncio
import discord
from discord import app_commands
from discord.ext import commands


class CookieView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=30)  # 30 seconds
        self.winner: discord.User | None = None

    @discord.ui.button(
        emoji="🍪", style=discord.ButtonStyle.success, custom_id="cookie_click"
    )
    async def cookie_click(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.winner = interaction.user
        self.cookie_click.disabled = True
        self.stop()

        await interaction.response.edit_message(
            content=f"> 🎉 {interaction.user.mention} clicked the cookie first! 🍪",
            view=self,
        )


class CookieCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="cookie", description="Click the cookie first")
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def cookie(self, interaction: discord.Interaction):
        # Initial reply
        await interaction.response.send_message(
            "> Get ready... Click the cookie in **5**"
        )

        # Countdown loop
        for i in range(4, 0, -1):
            await asyncio.sleep(1)
            try:
                await interaction.edit_original_response(
                    content=f"> Get ready... Click the cookie in **{i}**"
                )
            except discord.HTTPException:
                return  # Handle edge cases where interaction might be deleted/failed

        await asyncio.sleep(1)

        view = CookieView()
        msg = await interaction.edit_original_response(
            content="> **CLICK THE COOKIE!** 🍪", view=view
        )

        # Wait for interaction or timeout
        timed_out = await view.wait()

        if timed_out and not view.winner:
            view.cookie_click.disabled = True
            try:
                await interaction.edit_original_response(
                    content="> ⏰ Nobody clicked the cookie in time! 🍪", view=view
                )
            except discord.HTTPException:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(CookieCog(bot))
