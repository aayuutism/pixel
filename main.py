import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import discord
from discord.ext import commands
from dotenv import load_dotenv
from groups import ai_group, games_group, user_group

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True


class MyBot(commands.Bot):

    async def setup_hook(self):
        # Registering parent groups to the command tree first
        self.tree.add_command(games_group)
        self.tree.add_command(ai_group)
        self.tree.add_command(user_group)
        self.tree.add_command(family_group)

        # Automatically loading every extension/cog inside the cogs folder
        if os.path.exists("cogs"):
            for root, _, files in os.walk("cogs"):
                for file in files:
                    if file.endswith(".py") and not file.startswith("_") and file not in ("views.py", "database.py"):
                        rel_path = os.path.relpath(os.path.join(root, file), start=".")
                        cog_name = rel_path[:-3].replace(os.sep, ".")
                        
                        try:
                            await self.load_extension(cog_name)
                        except Exception as e:
                            print(f"Oops, failed to load {cog_name}: {e}")

      # Sync command tree with Discord
      # self.tree.clear_commands(guild=None)
        await self.tree.sync()
        print("All slash commands synced with Discord!")


bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    activity = discord.Streaming(
        name="Nothing suspicious going on here :3",
        url="https://www.youtube.com/watch?v=QDia3e12czc",
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"We're logged in as {bot.user} and ready to go!")


@bot.tree.error

async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    import traceback

    actual_error = getattr(error, "original", error)
    traceback.print_exception(type(actual_error), actual_error, actual_error.__traceback__)
    error_message = f"Welp, it's bitching. AGAIN: {type(actual_error).__name__}"
    
    if not interaction.response.is_done():
        await interaction.response.send_message(error_message, ephemeral=True)
    else:
        await interaction.followup.send(error_message, ephemeral=True)


class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is awake and chilling!")

    def log_message(self, format, *args):
        pass


def run_server():
    port = int(os.getenv("PORT", 3000))
    HTTPServer(("0.0.0.0", port), KeepAliveHandler).serve_forever()


if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    asyncio.run(bot.start(os.getenv("DISCORD_TOKEN")))
