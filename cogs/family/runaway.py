import random
import discord
from discord import app_commands
from discord.ext import commands
from . import database
from groups import family_group


class RunawaySelect(discord.ui.Select):

    def __init__(self, parent_members: list[discord.Member | discord.User], child_id: int, guild_id: int):
        self.child_id = child_id
        self.guild_id = guild_id

        options = [
            discord.SelectOption(
                label=parent.display_name,
                value=str(parent.id),
                description=f"ID: {parent.id}",
            )
            for parent in parent_members
        ]

        super().__init__(
            placeholder="Make a selection",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.child_id:
            return await interaction.response.send_message(
                "This menu isn't for you!", ephemeral=True
            )

        parent_id = int(self.values[0])
        await database.remove_adoption(
            parent_id=parent_id, child_id=self.child_id, guild_id=self.guild_id
        )

        embed = discord.Embed(
            description=f"You have run away from <@{parent_id}> :(",
            color=random.randint(0, 0xFFFFFF),
        )

        await interaction.response.edit_message(embed=embed, view=None)


class RunawayView(discord.ui.View):

    def __init__(self, parent_members: list[discord.Member | discord.User], child_id: int, guild_id: int):
        super().__init__(timeout=60)
        self.add_item(RunawaySelect(parent_members, child_id, guild_id))


class RunawayCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @family_group.command(
        name="runaway", description="Run away from one of your parents."
    )
    async def runaway(
        self,
        interaction: discord.Interaction,
        parent: discord.Member | None = None,
    ):
        if parent and parent.id == interaction.user.id:
            embed = discord.Embed(
                description="You cannot run away from yourself!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        # Fetch parents from database
        parents_ids = await database.get_parents(
            child_id=interaction.user.id, guild_id=guild_id
        )

        if not parents_ids:
            embed = discord.Embed(
                description="You don't have any parents to run away from!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Direct parent specified
        if parent:
            if parent.id not in parents_ids:
                embed = discord.Embed(
                    description=f"{parent.mention} is not your parent!",
                    color=random.randint(0, 0xFFFFFF),
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            await database.remove_adoption(
                parent_id=parent.id, child_id=interaction.user.id, guild_id=guild_id
            )
            embed = discord.Embed(
                description=f"You have run away from {parent.mention} :(",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(
                content=f"||{interaction.user.mention} {parent.mention}||",
                embed=embed,
            )

        # No parent specified -> show dropdown selection
        parent_members = []
        for parent_id in parents_ids:
            member = interaction.guild.get_member(parent_id) if interaction.guild else None
            if not member:
                try:
                    member = await self.bot.fetch_user(parent_id)
                except discord.HTTPException:
                    member = None
            if member:
                parent_members.append(member)

        if not parent_members:
            embed = discord.Embed(
                description="Could not resolve any of your parents' profiles.",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(
            description="Which parent do you want to run away from?",
            color=random.randint(0, 0xFFFFFF),
        )

        view = RunawayView(parent_members, interaction.user.id, guild_id)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(RunawayCog(bot))
