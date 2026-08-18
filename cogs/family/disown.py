import random
import discord
from discord import app_commands
from discord.ext import commands
from . import database

family_group = app_commands.Group(name="family", description="Family management commands")


class DisownSelect(discord.ui.Select):

    def __init__(self, children_members: list[discord.Member | discord.User], parent_id: int, guild_id: int):
        self.parent_id = parent_id
        self.guild_id = guild_id

        options = [
            discord.SelectOption(
                label=child.display_name,
                value=str(child.id),
                description=f"ID: {child.id}",
            )
            for child in children_members
        ]

        super().__init__(
            placeholder="Make a selection",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_id:
            return await interaction.response.send_message(
                "This menu isn't for you!", ephemeral=True
            )

        child_id = int(self.values[0])
        await database.remove_adoption(
            parent_id=self.parent_id, child_id=child_id, guild_id=self.guild_id
        )

        embed = discord.Embed(
            description=f"You have now disowned <@{child_id}> :(",
            color=random.randint(0, 0xFFFFFF),
        )

        # Edit original message to show final disowned embed and clear the dropdown menu
        await interaction.response.edit_message(embed=embed, view=None)


class DisownView(discord.ui.View):

    def __init__(self, children_members: list[discord.Member | discord.User], parent_id: int, guild_id: int):
        super().__init__(timeout=60)
        self.add_item(DisownSelect(children_members, parent_id, guild_id))


class DisownCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @family_group.command(name="disown", description="Disown one of your children.")
    async def disown(self, interaction: discord.Interaction):
        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        # Fetch children IDs from database
        children_ids = await database.get_children(
            parent_id=interaction.user.id, guild_id=guild_id
        )

        if not children_ids:
            embed = discord.Embed(
                description="You don't have any children to disown!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Resolve children IDs into Member/User objects
        children_members = []
        for child_id in children_ids:
            member = interaction.guild.get_member(child_id) if interaction.guild else None
            if not member:
                try:
                    member = await self.bot.fetch_user(child_id)
                except discord.HTTPException:
                    member = None
            if member:
                children_members.append(member)

        if not children_members:
            embed = discord.Embed(
                description="Could not resolve any of your children's user profiles.",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(
            description="Which of your children do you want to disown?",
            color=random.randint(0, 0xFFFFFF),
        )

        view = DisownView(children_members, interaction.user.id, guild_id)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    if not bot.tree.get_command("family"):
        bot.tree.add_command(family_group)
    await bot.add_cog(DisownCog(bot))
