import discord
from discord import app_commands
from discord.ext import commands


class AvatarCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="avatar", description="Shows the avatar of a member."
    )
    @app_commands.describe(
        target="The user whose avatar you want to see (optional)",
        avatar_type="Choose between Global or Server avatar (default: Global)",
    )
    @app_commands.choices(
        avatar_type=[
            app_commands.Choice(name="Global Avatar", value="global"),
            app_commands.Choice(name="Server Avatar", value="server"),
        ]
    )
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        target: discord.User | discord.Member | None = None,
        avatar_type: str = "global",
    ):
        target_user = target or interaction.user
        title = "Global Avatar"
        
        # Check if Server Avatar was requested
        if avatar_type == "server":
            # Check if target is a Member in a guild
            if isinstance(target_user, discord.Member) and target_user.guild_avatar:
                avatar_asset = target_user.guild_avatar
                title = f"Server Avatar ({interaction.guild.name})" if interaction.guild else "Server Avatar"
            else:
                # If target is not a Member (e.g. in DMs) or has no custom server avatar, fallback to display_avatar
                avatar_asset = target_user.display_avatar
                title = "Server Avatar (Fallback: Global)"
        else:
            # Default to Global Avatar
            avatar_asset = target_user.display_avatar

        avatar_url = avatar_asset.with_size(1024).url

        embed = discord.Embed(
            title=title, url=avatar_url, color=discord.Color.blue()
        )
        embed.set_author(
            name=target_user.name, icon_url=target_user.display_avatar.url
        )
        embed.set_image(url=avatar_url)

        # Link button to open the full-size image
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label=title,
                style=discord.ButtonStyle.link,
                url=avatar_url,
            )
        )

        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AvatarCog(bot))
