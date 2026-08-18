import discord
from discord import app_commands
from discord.ext import commands
from . import database
from .views import ProposalView

class MarryCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        await database.init_db()

    @app_commands.command(name="marry", description="Propose to another user.")
    async def marry(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot marry yourself!", ephemeral=True)
            return

        if user.bot:
            await interaction.response.send_message("You cannot marry a bot!", ephemeral=True)
            return

        view = ProposalView(requester=interaction.user, target=user)
        await interaction.response.send_message(
            content=f"💍 {user.mention}, {interaction.user.mention} has proposed to you! Do you accept?",
            view=view
        )

        await view.wait()

        if view.accepted:
            is_guild_specific = await database.get_guild_setting(interaction.guild_id)
            guild_id = interaction.guild_id if is_guild_specific else 0
            await database.add_marriage(interaction.user.id, user.id, guild_id)

async def setup(bot: commands.Bot):
    await bot.add_cog(MarryCog(bot))
