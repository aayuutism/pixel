import discord
from discord import app_commands
from discord.ext import commands
from . import database
from .views import ProposalView

class AdoptCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="adopt", description="Ask to adopt another user.")
    async def adopt(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot adopt yourself!", ephemeral=True)
            return

        if user.bot:
            await interaction.response.send_message("You cannot adopt a bot!", ephemeral=True)
            return

        view = ProposalView(requester=interaction.user, target=user)
        await interaction.response.send_message(
            content=f"👶 {user.mention}, {interaction.user.mention} wants to adopt you! Do you accept?",
            view=view
        )

        await view.wait()

        if view.accepted:
            is_guild_specific = await database.get_guild_setting(interaction.guild_id)
            guild_id = interaction.guild_id if is_guild_specific else 0
            await database.add_adoption(parent_id=interaction.user.id, child_id=user.id, guild_id=guild_id)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdoptCog(bot))
