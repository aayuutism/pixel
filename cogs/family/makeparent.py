import discord
from discord import app_commands
from discord.ext import commands
from . import database
from .views import ProposalView

class MakeParentCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="makeparent", description="Ask to make another user into your parent.")
    async def makeparent(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot make yourself your own parent!", ephemeral=True)
            return

        if user.bot:
            await interaction.response.send_message("You cannot make a bot your parent!", ephemeral=True)
            return

        view = ProposalView(requester=interaction.user, target=user)
        await interaction.response.send_message(
            content=f"👨‍👧 {user.mention}, {interaction.user.mention} wants to become your child! Do you accept?",
            view=view
        )

        await view.wait()

        if view.accepted:
            is_guild_specific = await database.get_guild_setting(interaction.guild_id)
            guild_id = interaction.guild_id if is_guild_specific else 0
            # Target becomes parent, interaction.user becomes child
            await database.add_adoption(parent_id=user.id, child_id=interaction.user.id, guild_id=guild_id)

async def setup(bot: commands.Bot):
    await bot.add_cog(MakeParentCog(bot))
