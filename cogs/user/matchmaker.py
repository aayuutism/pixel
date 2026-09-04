import discord
from discord import app_commands
from discord.ext import commands

class ChatControlView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)  # Persistent view
        self.bot = bot
        # Queue storing user IDs waiting for a random chat
        self.waiting_queue = []

    # Helper to determine current state of a user
    def get_user_state(self, user_id: int, interaction: discord.Interaction) -> str:
        # Check if user is in an active channel managed by this system
        # (We can check channel topic or category for simplicity)
        if interaction.channel.topic and f"owner:{user_id}" in interaction.channel.topic:
            return "in_chat"
        if user_id in self.waiting_queue:
            return "waiting"
        return "idle"

    @discord.ui.button(label="Random Chat", style=discord.ButtonStyle.primary, custom_id="chat_random_btn", row=0)
    async def random_chat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # 1. If waiting, cancel wait
        if user.id in self.waiting_queue:
            self.waiting_queue.remove(user.id)
            button.label = "Random Chat"
            button.style = discord.ButtonStyle.primary
            
            # Re-enable specific chat button
            for child in self.children:
                if child.custom_id == "chat_specific_btn":
                    child.disabled = False
                    
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send("You have left the matchmaking queue.", ephemeral=True)

        # 2. If in active chat, skip chat
        # (We'll implement channel cleanup/rematch logic here shortly)

        # 3. Otherwise, join queue
        if len(self.waiting_queue) > 0:
            partner_id = self.waiting_queue.pop(0)
            partner = interaction.guild.get_member(partner_id)
            
            if not partner:
                # Fallback if cached partner left
                self.waiting_queue.append(user.id)
                button.label = "Cancel Wait"
                button.style = discord.ButtonStyle.danger
                await interaction.response.edit_message(view=self)
                return await interaction.followup.send("No valid partner found. You are now waiting in the queue.", ephemeral=True)

            # Create private channel for the pair
            await self.create_private_chat(interaction, user, partner)
        else:
            self.waiting_queue.append(user.id)
            button.label = "Cancel Wait"
            button.style = discord.ButtonStyle.danger
            
            # Disable specific chat while waiting
            for child in self.children:
                if child.custom_id == "chat_specific_btn":
                    child.disabled = True

            await interaction.response.edit_message(view=self)
            await interaction.response.send_message("Joined the random chat queue. Waiting for a partner...", ephemeral=True)

    @discord.ui.button(label="Specific Chat", style=discord.ButtonStyle.secondary, custom_id="chat_specific_btn", row=0)
    async def specific_chat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Trigger user selection modal or dropdown
        await interaction.response.send_message("Specific chat selection coming up...", ephemeral=True)

    async def create_private_chat(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user1: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            user2: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        # Optional: Place inside a specific category if you have one
        channel = await guild.create_text_channel(
            name=f"chat-{user1.name}-{user2.name}",
            overwrites=overwrites,
            topic=f"owner:{user1.id} owner:{user2.id}"
        )
        
        await interaction.response.send_message(f"Match found! Head over to {channel.mention}.", ephemeral=True)
        await channel.send(f"Private chat started between {user1.mention} and {user2.mention}!")


class ChatMatchmakerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.bot.add_view(ChatControlView(self.bot))
            self.persistent_views_added = True

    @app_commands.command(name="setupchat", description="Deploy the chat matchmaker control panel.")
    async def setupchat(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "**Pixel Chat Matchmaking**\nClick below to start chatting randomly or with a specific user.",
            view=ChatControlView(self.bot)
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ChatMatchmakerCog(bot))
