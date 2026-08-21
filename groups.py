from discord import app_commands

family_group = app_commands.Group(name="family", description="family")
user_group = app_commands.Group(name="user", description="user")
games_group = app_commands.Group(name="games", description="games")
ai_group = app_commands.Group(name="ai", description="ai")

async def setup(bot): pass
