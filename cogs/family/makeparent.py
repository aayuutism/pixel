import random
import discord
from discord import app_commands
from discord.ext import commands
from . import database
from .groups import family_group
from .views import ProposalView


class MakeParentCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @family_group.command(
        name="makeparent", description="Ask to make another user into your parent."
    )
    async def makeparent(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            embed = discord.Embed(
                description="You cannot make yourself your own parent!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if user.bot:
            embed = discord.Embed(
                description="You cannot make a bot your parent!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        # Check existing children count for the proposed parent
        target_children = await database.get_children(
            parent_id=user.id, guild_id=guild_id
        )
        if target_children and len(target_children) >= 6:
            embed = discord.Embed(
                description=f"{user.mention} already has 6 children! They can't adopt any more right now :<",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Proposal Embed
        embed = discord.Embed(
            description=f"Hey {user.mention}, {interaction.user.mention} wants you to be their parent! What do you say?",
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
            # Target becomes parent, interaction.user becomes child
            await database.add_adoption(parent_id=user.id, child_id=interaction.user.id, guild_id=guild_id)


async def setup(bot: commands.Bot):
    await bot.add_cog(MakeParentCog(bot))
