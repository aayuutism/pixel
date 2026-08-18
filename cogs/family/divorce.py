import random
import discord
from discord import app_commands
from discord.ext import commands
from . import database
from groups import family_group


class DivorceSelect(discord.ui.Select):

    def __init__(self, partner_members: list[discord.Member | discord.User], user_id: int, guild_id: int):
        self.user_id = user_id
        self.guild_id = guild_id

        options = [
            discord.SelectOption(
                label=partner.display_name,
                value=str(partner.id),
                description=f"ID: {partner.id}",
            )
            for partner in partner_members
        ]

        super().__init__(
            placeholder="Make a selection",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "This menu isn't for you!", ephemeral=True
            )

        partner_id = int(self.values[0])
        await database.remove_marriage(
            user1_id=self.user_id, user2_id=partner_id, guild_id=self.guild_id
        )

        embed = discord.Embed(
            description=f"You have divorced <@{partner_id}> :(",
            color=random.randint(0, 0xFFFFFF),
        )

        await interaction.response.edit_message(embed=embed, view=None)


class DivorceView(discord.ui.View):

    def __init__(self, partner_members: list[discord.Member | discord.User], user_id: int, guild_id: int):
        super().__init__(timeout=60)
        self.add_item(DivorceSelect(partner_members, user_id, guild_id))


class DivorceCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @family_group.command(name="divorce", description="Divorce one of your partners.")
    async def divorce(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ):
        if user and user.id == interaction.user.id:
            embed = discord.Embed(
                description="You cannot divorce yourself!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        is_guild_specific = await database.get_guild_setting(interaction.guild_id)
        guild_id = interaction.guild_id if is_guild_specific else 0

        # Fetch partners from database
        partners_ids = await database.get_partners(
            user_id=interaction.user.id, guild_id=guild_id
        )

        if not partners_ids:
            embed = discord.Embed(
                description="You aren't married to anyone!",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Direct target specified
        if user:
            if user.id not in partners_ids:
                embed = discord.Embed(
                    description=f"You aren't married to {user.mention}!",
                    color=random.randint(0, 0xFFFFFF),
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            await database.remove_marriage(interaction.user.id, user.id, guild_id)
            embed = discord.Embed(
                description=f"You have divorced {user.mention} :(",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(
                content=f"||{interaction.user.mention} {user.mention}||",
                embed=embed,
            )

        # No target specified -> show select dropdown menu
        partner_members = []
        for partner_id in partners_ids:
            member = interaction.guild.get_member(partner_id) if interaction.guild else None
            if not member:
                try:
                    member = await self.bot.fetch_user(partner_id)
                except discord.HTTPException:
                    member = None
            if member:
                partner_members.append(member)

        if not partner_members:
            embed = discord.Embed(
                description="Could not resolve any of your partners' profiles.",
                color=random.randint(0, 0xFFFFFF),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(
            description="Which of your partners do you want to divorce?",
            color=random.randint(0, 0xFFFFFF),
        )

        view = DivorceView(partner_members, interaction.user.id, guild_id)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(DivorceCog(bot))
