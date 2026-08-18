from discord import app_commands

family_group = app_commands.Group(name="family", description="Family-related commands")
user_group = app_commands.Group(name="user", description="User-related commands")
games_group = app_commands.Group(name="games", description="Play various mini-games!")
ai_group = app_commands.Group(name="ai", description="AI based commands")

async def setup(bot): pass
