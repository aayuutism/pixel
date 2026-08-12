import discord
from discord import app_commands
from discord.ext import commands


# Custom View for the button interaction
class EchoButtonView(discord.ui.View):
    def __init__(self, author: discord.User | discord.Member):
        super().__init__(timeout=None)  # Keeps button persistent
        self.author = author

    @discord.ui.button(
        label="Sent using echo",
        style=discord.ButtonStyle.primary,  # Makes the button blue
        custom_id="echo_sent_by_button",
    )
    async def echo_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # Replies back with the "Sent by: @user" message (only visible to the clicker)
        await interaction.response.send_message(
            f"*Sent by:* {self.author.mention}", ephemeral=True
        )


class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="echo",
        description="Makes the bot say something in the specified channel",
    )
    @app_commands.describe(
        message="The message you want the bot to say",
        channel="Input text channel (optional)",
        show_button="Attach the 'Sent using echo' button (default: False)",
    )
    async def echo(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: discord.TextChannel | None = None,
        show_button: bool = False,
    ):
        target_channel = channel or interaction.channel

        if not target_channel or not isinstance(
            target_channel, discord.TextChannel
        ):
            await interaction.response.send_message(
                "Invalid channel selected.", ephemeral=True
            )
            return

        permissions = target_channel.permissions_for(interaction.user)
        if not permissions.send_messages:
            await interaction.response.send_message(
                f"You don't have permission to send messages in {target_channel.mention}!",
                ephemeral=True,
            )
            return

        # Attach view if show_button is True
        view = EchoButtonView(author=interaction.user) if show_button else None

        if view:
            await target_channel.send(content=message, view=view)
        else:
            await target_channel.send(content=message)

        # Confirm message sent silently to the sender
        await interaction.response.send_message("Sent!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))
