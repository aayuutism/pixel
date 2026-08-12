import discord
from discord import app_commands
from discord.ext import commands


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
        no_button="Toggle *Sent using echo* button (optional)",
    )
    async def echo(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: discord.TextChannel | None = None,
        no_button: bool = False,
    ):
        # Target specified channel, or default to current channel
        target_channel = channel or interaction.channel

        if not target_channel or not isinstance(
            target_channel, discord.TextChannel
        ):
            await interaction.response.send_message(
                "Invalid channel selected.", ephemeral=True
            )
            return

        # Check permissions before sending
        permissions = target_channel.permissions_for(interaction.user)
        if not permissions.send_messages:
            await interaction.response.send_message(
                f"You don't have permission to send messages in {target_channel.mention}!",
                ephemeral=True,
            )
            return

        # Prepare view/button if requested
        view = None
        if not no_button:
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    label="Sent using echo",
                    disabled=True,
                    style=discord.ButtonStyle.secondary,
                )
            )

        # Send message to target channel
        if view:
            await target_channel.send(content=message, view=view)
        else:
            await target_channel.send(content=message)

        # Acknowledge execution silently to the command user
        await interaction.response.send_message(
            f"Message sent to {target_channel.mention}!", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))
