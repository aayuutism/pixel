import io
import re
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


class StealModal(discord.ui.Modal, title="Name Your New Emoji"):
    emoji_name = discord.ui.TextInput(
        label="Emoji Name",
        placeholder="Enter a name for the emoji...",
        min_length=2,
        max_length=32,
    )

    def __init__(self, image_bytes: bytes):
        super().__init__()
        self.image_bytes = image_bytes

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message(
                "This command can only be used inside a server.", ephemeral=True
            )

        if not guild.me.guild_permissions.manage_emojis:
            return await interaction.response.send_message(
                "I don't have the **Manage Emojis and Stickers** permission in this server.",
                ephemeral=True,
            )

        try:
            new_emoji = await guild.create_custom_emoji(
                name=self.emoji_name.value, image=self.image_bytes
            )
            await interaction.response.send_message(
                f"Successfully added {new_emoji} to the server!", ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"Failed to create emoji: {e.text}", ephemeral=True
            )


class StealView(discord.ui.View):

    def __init__(self, image_url: str, image_bytes: bytes):
        super().__init__(timeout=180)
        self.image_url = image_url
        self.image_bytes = image_bytes

    @discord.ui.button(label="Add as Emoji", style=discord.ButtonStyle.primary)
    async def add_emoji(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not interaction.guild:
            return await interaction.response.send_message(
                "This can only be used in a server.", ephemeral=True
            )
        await interaction.response.send_modal(StealModal(self.image_bytes))

    @discord.ui.button(label="Add as Sticker", style=discord.ButtonStyle.primary)
    async def add_sticker(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message(
                "This can only be used in a server.", ephemeral=True
            )

        if not guild.me.guild_permissions.manage_emojis:
            return await interaction.response.send_message(
                "I don't have the **Manage Emojis and Stickers** permission.",
                ephemeral=True,
            )

        try:
            file = discord.File(
                io.BytesIO(self.image_bytes), filename="sticker.png"
            )
            new_sticker = await guild.create_sticker(
                name="stolen_sticker",
                description="Stolen via /steal",
                emoji="✨",
                file=file,
            )
            await interaction.response.send_message(
                f"Successfully added sticker **{new_sticker.name}**!", ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"Failed to create sticker: {e.text}", ephemeral=True
            )


class StealCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="steal", description="Add an emoji or a sticker to the server."
    )
    @app_commands.describe(source="The source of the emoji or sticker.")
    async def steal(self, interaction: discord.Interaction, source: str):
        await interaction.response.defer(ephemeral=True)

        image_url = None

        # 1. Check if it's a custom Discord emoji string like <:name:id> or <a:name:id>
        custom_emoji_match = re.match(r"<a?:\w+:(\d+)>", source)
        if custom_emoji_match:
            emoji_id = custom_emoji_match.group(1)
            is_animated = source.startswith("<a:")
            ext = "gif" if is_animated else "png"
            image_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"

        # 2. Check if it's a raw URL
        elif source.startswith("http://") or source.startswith("https://"):
            image_url = source

        if not image_url:
            return await interaction.followup.send(
                "Please provide a valid custom emoji or an image URL.", ephemeral=True
            )

        # Download the image bytes
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return await interaction.followup.send(
                        "Failed to fetch the image from the provided source.",
                        ephemeral=True,
                    )
                image_bytes = await resp.read()

        view = StealView(image_url, image_bytes)
        await interaction.followup.send(
            content=image_url, view=view, ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(StealCog(bot))
