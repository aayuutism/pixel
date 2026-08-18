import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

# Reuse the shared group if it exists, or create it if this file runs standalone
if not 'games_group' in globals():
    games_group = app_commands.Group(name="games", description="Play various mini-games!")


class MoleButton(discord.ui.Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="🕳️", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: WhackAMoleView = self.view

        # Avoid double-clicking during transition
        if view.action_taken:
            return

        # 1. Clicked a Mole
        if self.label == "🐹":
            view.action_taken = True
            view.score += 1
            self.label = "🎯"
            self.style = discord.ButtonStyle.success
            
            for child in view.children:
                child.disabled = True

            await interaction.response.edit_message(
                content=f"✨ **WHACK!** Score: **{view.score}** | Strikes: **{view.strikes}/{view.max_strikes}**", 
                view=view
            )

        # 2. Clicked a Bomb
        elif self.label == "💣":
            view.action_taken = True
            view.strikes += 1
            self.label = "💥"
            self.style = discord.ButtonStyle.danger
            
            for child in view.children:
                child.disabled = True

            await interaction.response.edit_message(
                content=f"💣 **BOOM!** You hit a bomb! Strikes: **{view.strikes}/{view.max_strikes}**", 
                view=view
            )

        # 3. Clicked an Empty Hole
        else:
            await interaction.response.send_message("That's just an empty hole! 🕳️", ephemeral=True)


class WhackAMoleView(discord.ui.View):
    def __init__(self, author_id: int, max_strikes: int = 5):
        super().__init__(timeout=120.0)
        self.author_id = author_id
        self.score = 0
        self.strikes = 0
        self.max_strikes = max_strikes
        self.action_taken = False

        # Build 3x3 grid
        for y in range(3):
            for x in range(3):
                self.add_item(MoleButton(x, y))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Start your own game with `/games whackamole`!", ephemeral=True)
            return False
        return True


class WhackAMoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @games_group.command(name="whackamole", description="Whack moles, avoid bombs, and survive!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def whackamole(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        max_strikes = 5
        view = WhackAMoleView(author_id=interaction.user.id, max_strikes=max_strikes)
        
        await interaction.followup.send(
            content=f"🎮 **Whack-a-Mole Starting!**\nAvoid 💣 bombs and don't miss 🐹 moles! Max Strikes: **{max_strikes}**", 
            view=view
        )

        round_num = 0

        while view.strikes < max_strikes:
            round_num += 1
            view.action_taken = False

            # Reset all grid buttons to empty holes
            for child in view.children:
                child.label = "🕳️"
                child.style = discord.ButtonStyle.secondary
                child.disabled = False

            # Decide what spawns this round:
            # 70% chance for Mole, 30% chance for Bomb
            spawn_type = random.choices(["mole", "bomb"], weights=[70, 30])[0]

            # Pick a random hole to spawn in
            target_button: MoleButton = random.choice(view.children)

            if spawn_type == "mole":
                target_button.label = "🐹"
                target_button.style = discord.ButtonStyle.primary
                prompt = "🐹 **A mole appeared! WHACK IT!**"
            else:
                target_button.label = "💣"
                target_button.style = discord.ButtonStyle.secondary
                prompt = "💣 **A BOMB appeared! DON'T CLICK IT!**"

            await interaction.edit_original_response(
                content=f"{prompt}\nScore: **{view.score}** | Strikes: **{view.strikes}/{max_strikes}**",
                view=view
            )

            # Wait 1.5 seconds for player reaction
            await asyncio.sleep(1.5)

            # If it was a mole and the user missed it -> Strike!
            if spawn_type == "mole" and not view.action_taken:
                view.strikes += 1
                for child in view.children:
                    child.disabled = True
                
                await interaction.edit_original_response(
                    content=f"💨 **Too slow! The mole escaped!** (+1 Strike)\nScore: **{view.score}** | Strikes: **{view.strikes}/{max_strikes}**",
                    view=view
                )
                await asyncio.sleep(1.0)

            # If it was a bomb and they successfully avoided it -> Good job!
            elif spawn_type == "bomb" and not view.action_taken:
                for child in view.children:
                    child.disabled = True

                await interaction.edit_original_response(
                    content=f"⚡ **Safe! You avoided the bomb!**\nScore: **{view.score}** | Strikes: **{view.strikes}/{max_strikes}**",
                    view=view
                )
                await asyncio.sleep(0.8)

            else:
                # User clicked either mole or bomb during the turn
                await asyncio.sleep(0.8)

        # Game Over state
        for child in view.children:
            child.disabled = True
            child.label = "🕳️"
            child.style = discord.ButtonStyle.secondary

        await interaction.edit_original_response(
            content=f"# 💥 **Game Over!**\nYou hit maximum strikes (**{max_strikes}/{max_strikes}**).\n> Final Score: **{view.score}** moles whacked across **{round_num}** rounds!",
            view=view
        )

async def setup(bot: commands.Bot):
    if not bot.tree.get_command("games"):
        bot.tree.add_command(games_group)
    if not bot.get_cog("WhackAMoleCog"):
        await bot.add_cog(WhackAMoleCog(bot))
