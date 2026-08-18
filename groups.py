from groups import family_group, user_group, games_group

if not self.tree.get_command("family"):
    self.tree.add_command(family_group)
    
if not self.tree.get_command("user"):
    self.tree.add_command(user_group)
    
if not self.tree.get_command("games"):
    self.tree.add_command(games_group)
    
async def setup(bot):
    pass
