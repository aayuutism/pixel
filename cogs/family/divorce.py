import discord
from discord import app_commands
from discord.ext import commands
from . import database

class DivorceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="divorce", description="Divorce one of your partners.")
    async def divorce(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot divorce yourself!", ephemeral=True)
            return

        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        await database.remove_marriage(interaction.user.id, user.id, guild_id)
        
        await interaction.response.send_message(
            f"💔 {interaction.user.mention} has divorced {user.mention}."
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(DivorceCog(bot))
