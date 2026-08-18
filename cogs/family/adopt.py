import random
import discord
from discord import app_commands
from discord.ext import commands
from . import database
from .views import ProposalView

family_group = app_commands.Group(name="family", description="Family management commands")


class AdoptCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @family_group.command(name="adopt", description="Ask to adopt another user.")
    async def adopt(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            embed = discord.Embed(
                description="You cannot adopt yourself!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if user.bot:
            embed = discord.Embed(
                description="You cannot adopt a bot!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        # Check existing children count
        existing_children = await database.get_children(
            parent_id=interaction.user.id, guild_id=guild_id
        )
        if existing_children and len(existing_children) >= 6:
            embed = discord.Embed(
                description="You already have 6 children! You can't have any more right now :<",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Proposal Embed
        embed = discord.Embed(
            description=f"Hey {user.mention}, {interaction.user.mention} wants to adopt you! What do you say?",
            color=random.randint(0, 0xFFFFFF),
        )

        view = ProposalView(requester=interaction.user, target=user)

        # Spoiler ping outside the embed so both users get notified
        await interaction.response.send_message(
            content=f"||{user.mention} {interaction.user.mention}||",
            embed=embed,
            view=view,
        )

        await view.wait()

        if view.accepted:
            await database.add_adoption(parent_id=interaction.user.id, child_id=user.id, guild_id=guild_id)


async def setup(bot: commands.Bot):
    if not bot.tree.get_command("family"):
        bot.tree.add_command(family_group)
    await bot.add_cog(AdoptCog(bot))
