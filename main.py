import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()

# Initialize Bot Client with required intents (and DM support)
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.direct_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


# Helper function to recursively load command files (Cogs) from subfolders
async def load_commands(directory: str):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                # Convert path to module format (e.g. commands/games/ship.py -> commands.games.ship)
                rel_path = os.path.relpath(os.path.join(root, file), start=".")
                module_name = rel_path[:-3].replace(os.sep, ".")
                try:
                    await bot.load_extension(module_name)
                    print(f"Loaded extension: {module_name}")
                except Exception as e:
                    print(f"Failed to load extension {module_name}: {e}")


@bot.event
async def on_ready():
    # Sync slash commands with Discord API upon startup
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

    print(f"Logged in as {bot.user} (Python Bot Live!)")


# Keep-alive HTTP server for Render port check
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is awake!")

    def log_message(self, format, *args):
        return  # Silence standard HTTP server logs in console


def run_http_server():
    port = int(os.getenv("PORT", 3000))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    server.serve_forever()


# Run keep-alive server in a background thread
Thread(target=run_http_server, daemon=True).start()


async def main():
    async with bot:
        # Load commands from 'commands' directory if it exists
        if os.path.exists("commands"):
            await load_commands("commands")

        await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
