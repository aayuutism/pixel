import re
import discord
from discord import app_commands
from discord.ext import commands

EMOJI_REGEX = re.compile(r"<?(?:a)?:?\w+:(\d{17,20})>?")


class EmojiCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="emoji",
        description="Get the full size image/GIF of a custom emoji.",
    )
    @app_commands.describe(
        emoji="The emoji (<:name:id> or animated) or just its ID"
    )
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def emoji_cmd(self, interaction: discord.Interaction, emoji: str):
        emoji_id = None

        # Check if the input is a formatted emoji or raw ID
        match = EMOJI_REGEX.search(emoji)
        if match:
            emoji_id = int(match.group(1))
        elif emoji.isdigit():
            emoji_id = int(emoji)

        if not emoji_id:
            return await interaction.response.send_message(
                content="> ⚠️ Invalid custom emoji or emoji ID provided.",
                ephemeral=True,
            )

        # Determine if emoji is animated
        is_animated = emoji.startswith("<a:")

        # Try to resolve PartialEmoji or custom emoji object
        emoji_obj = self.bot.get_emoji(
            emoji_id
        ) or discord.PartialEmoji.from_str(emoji)

        if emoji_obj and emoji_obj.is_custom_emoji():
            emoji_url = emoji_obj.url
        else:
            # Fallback URL construction
            extension = "gif" if is_animated else "png"
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{extension}?size=1024"

        await interaction.response.send_message(content=emoji_url)


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiCog(bot))
