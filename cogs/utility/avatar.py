import discord
from discord import app_commands
from discord.ext import commands

user_group = app_commands.Group(name="user", description="User utility commands")


class AvatarCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @user_group.command(
        name="avatar", description="Shows the avatar of a member."
    )
    @app_commands.describe(
        target="The user whose avatar you want to see (optional)"
    )
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        target: discord.User | None = None,
    ):
        target_user = target or interaction.user
        avatar_url = target_user.display_avatar.with_size(1024).url

        embed = discord.Embed(
            title="Global Avatar", url=avatar_url, color=discord.Color.blue()
        )
        embed.set_author(
            name=target_user.name, icon_url=target_user.display_avatar.url
        )
        embed.set_image(url=avatar_url)

        # Link button to open the full-size image
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Global Avatar",
                style=discord.ButtonStyle.link,
                url=avatar_url,
            )
        )

        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )


async def setup(bot: commands.Bot):
    if not bot.tree.get_command("user"):
        bot.tree.add_command(user_group)
    await bot.add_cog(AvatarCog(bot))
