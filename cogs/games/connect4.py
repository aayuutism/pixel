class ConnectFourCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="connect4", description="Play Connect Four with a friend")
    @app_commands.describe(player="Pick who you wanna play against!")
    async def connectfour(self, interaction: discord.Interaction, player: discord.User | None = None):
        await interaction.response.defer()

        if player and player.id == interaction.user.id:
            return await interaction.followup.send("You really wanna play against yourself?", ephemeral=True)
        if player and player.bot:
            return await interaction.followup.send("Oi, pick a real person to play with.", ephemeral=True)

        invite_view = ConnectFourInviteView(interaction.user, player)
        target_mention = player.mention if player else "Anyone"
        
        invite_embed = discord.Embed(
            title="Connect Four Invitation",
            description=f"Join {interaction.user.mention} in Connect Four!\nWaiting for: {target_mention}",
            color=discord.Color(0x131416)
        )
        
        msg = await interaction.followup.send(embed=invite_embed, view=invite_view)

        if await invite_view.wait() or not invite_view.accepted:
            for child in invite_view.children:
                child.disabled = True
            timeout_embed = discord.Embed(
                title="Connect Four Invitation",
                description=f"{TIMER} **Aw, the invitation timed out.**",
                color=discord.Color(0x131416)
            )
            return await msg.edit(embed=timeout_embed, view=invite_view)

        board_view = ConnectFourBoardView(interaction.user, invite_view.opponent)
        board_embed = board_view.get_embed(f"{PLAYER1} {interaction.user.mention}, it's your turn!")
        
        await msg.edit(
            embed=board_embed,
            view=board_view,
        )

        if await board_view.wait():
            board_view.update_buttons(disabled=True)
            timeout_game_embed = board_view.get_embed(f"{TIMER} Aw, the game timed out due to inactivity.")
            await msg.edit(
                embed=timeout_game_embed, view=board_view
            )
