import discord
from discord import app_commands
from discord.ext import commands
from . import database

class DisownCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="disown", description="Disown one of your children.")
    async def disown(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot disown yourself!", ephemeral=True)
            return

        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        await database.remove_adoption(parent_id=interaction.user.id, child_id=user.id, guild_id=guild_id)

        await interaction.response.send_message(
            f"🚫 {interaction.user.mention} has disowned {user.mention}."
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(DisownCog(bot))
