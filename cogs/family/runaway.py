import discord
from discord import app_commands
from discord.ext import commands
from . import database

class RunawayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="runaway", description="Run away from one of your parents.")
    async def runaway(self, interaction: discord.Interaction, parent: discord.Member):
        if parent.id == interaction.user.id:
            await interaction.response.send_message("You cannot run away from yourself!", ephemeral=True)
            return

        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        # interaction.user is the child, parent is the parent_id
        await database.remove_adoption(parent_id=parent.id, child_id=interaction.user.id, guild_id=guild_id)

        await interaction.response.send_message(
            f"🏃 {interaction.user.mention} has run away from their parent {parent.mention}!"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(RunawayCog(bot))
