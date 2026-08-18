import discord

class ProposalView(discord.ui.View):
    def __init__(self, requester: discord.Member, target: discord.Member, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.requester = requester
        self.target = target
        self.accepted = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Ensure only the targeted user can click the buttons
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                f"Only {self.target.mention} can respond to this request!",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.accepted = True
        self.stop()
        # Disable all buttons after interaction
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=f"❤️ {self.target.mention} accepted {self.requester.mention}'s request!",
            view=self
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.accepted = False
        self.stop()
        # Disable all buttons after interaction
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=f"💔 {self.target.mention} declined {self.requester.mention}'s request.",
            view=self
        )

    async def on_timeout(self):
        # Disable buttons if no one responds within 60 seconds
        for item in self.children:
            item.disabled = True
        self.accepted = False
