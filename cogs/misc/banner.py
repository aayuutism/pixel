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
        target="The user whose banner you want to see (optional)"
    )
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def banner(
        self,
        interaction: discord.Interaction,
        target: discord.User | None = None,
    ):
        target_user = target or interaction.user

        # Fetch the complete user profile to ensure banner data is available
        user = await self.bot.fetch_user(target_user.id)

        if not user.banner:
            return await interaction.response.send_message(
                content=f"> ⚠️ {interaction.user.mention}: {user.mention} doesn't have a banner.",
                ephemeral=True,
            )

        banner_url = user.banner.with_size(1024).url

        embed = discord.Embed(
            title="User Banner",
            url=banner_url,
            color=discord.Color.from_str("#1E88E5"),
        )
        embed.set_author(
            name=user.name, icon_url=user.display_avatar.url
        )
        embed.set_image(url=banner_url)

        # Link button to view/download high-res banner
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="User Banner",
                style=discord.ButtonStyle.link,
                url=banner_url,
            )
        )

        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(BannerCog(bot))
