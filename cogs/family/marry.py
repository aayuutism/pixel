import random
import discord
from discord import app_commands
from discord.ext import commands
from . import database
from .views import ProposalView

family_group = app_commands.Group(name="family", description="Family management commands")


class MarryCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        await database.init_db()

    @family_group.command(name="marry", description="Propose to another user.")
    async def marry(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            embed = discord.Embed(
                description="You cannot marry yourself!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if user.bot:
            embed = discord.Embed(
                description="You cannot marry a bot!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        # Check partner count for requester
        requester_partners = await database.get_partners(
            user_id=interaction.user.id, guild_id=guild_id
        )
        if requester_partners and len(requester_partners) >= 2:
            embed = discord.Embed(
                description="You already have 2 partners! You can't marry anyone else right now :<",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Check partner count for target user
        target_partners = await database.get_partners(
            user_id=user.id, guild_id=guild_id
        )
        if target_partners and len(target_partners) >= 2:
            embed = discord.Embed(
                description=f"{user.mention} already has 2 partners!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Proposal Embed
        embed = discord.Embed(
            description=f"Hey {user.mention}, {interaction.user.mention} has proposed to you! What do you say?",
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
            await database.add_marriage(interaction.user.id, user.id, guild_id)


async def setup(bot: commands.Bot):
    if not bot.tree.get_command("family"):
        bot.tree.add_command(family_group)
    await bot.add_cog(MarryCog(bot))
