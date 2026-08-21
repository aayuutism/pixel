from discord import app_commands

family_group = app_commands.Group(name="family")
user_group = app_commands.Group(name="user")
games_group = app_commands.Group(name="games")
ai_group = app_commands.Group(name="ai")

async def setup(bot): pass
