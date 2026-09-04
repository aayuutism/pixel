import discord
from discord import app_commands
from discord.ext import commands


class BannerCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="banner", description="Shows the user banner of a member."
    )
    @app_commands.describe(
        target="The user whose banner you want to see (optional)",
        banner_type="Choose between Global or Server banner (default: Global)",
    )
    @app_commands.choices(
        banner_type=[
            app_commands.Choice(name="Global Banner", value="global"),
            app_commands.Choice(name="Server Banner", value="server"),
        ]
    )
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def banner(
        self,
        interaction: discord.Interaction,
        target: discord.User | discord.Member | None = None,
        banner_type: str = "global",
    ):
        target_user = target or interaction.user
        title = "User Banner"
        banner_asset = None

        # Handle Server Banner requested
        if banner_type == "server" and interaction.guild:
            try:
                # Fetch full member object to get server profile/banner data
                member = await interaction.guild.fetch_member(target_user.id)
                if member and member.guild_banner:
                    banner_asset = member.guild_banner
                    title = f"Server Banner ({interaction.guild.name})"
            except discord.HTTPException:
                pass

        # Fallback / Default to Global Banner
        if not banner_asset:
            user = await self.bot.fetch_user(target_user.id)
            if user.banner:
                banner_asset = user.banner
                if banner_type == "server":
                    title = "Server Banner (Fallback: Global)"

        # If no banner is set anywhere
        if not banner_asset:
            return await interaction.response.send_message(
                content=f"> ⚠️ {interaction.user.mention}: {target_user.mention} doesn't have a banner.",
                ephemeral=True,
            )

        banner_url = banner_asset.with_size(1024).url

        embed = discord.Embed(
            title=title,
            url=banner_url,
            color=discord.Color.from_str("#1E88E5"),
        )
        embed.set_author(
            name=target_user.name, icon_url=target_user.display_avatar.url
        )
        embed.set_image(url=banner_url)

        # Link button to view/download high-res banner
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label=title,
                style=discord.ButtonStyle.link,
                url=banner_url,
            )
        )

        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(BannerCog(bot))
