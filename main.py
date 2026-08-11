import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from threading import Thread

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Bot Client with required intents (including Presences for status display)
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.dm_messages = True
intents.presences = True  # Required to broadcast presence/status properly

bot = commands.Bot(command_prefix="!", intents=intents)


# Helper function to recursively load command files (Cogs) from subfolders
async def load_commands(directory: str):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                # Convert path to module format (e.g. cogs/utility/ship.py -> cogs.utility.ship)
                rel_path = os.path.relpath(os.path.join(root, file), start=".")
                module_name = rel_path[:-3].replace(os.sep, ".")
                try:
                    await bot.load_extension(module_name)
                    print(f"Loaded extension: {module_name}")
                except Exception as e:
                    print(f"Failed to load extension {module_name}: {e}")


@bot.event
async def on_ready():
    # --- STREAMING PRESENCE ---
    streaming_activity = discord.Streaming(
        name="Nothing suspicious going on here :3",
        state="don't click watch",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )

    await bot.change_presence(
        status=discord.Status.online,
        activity=streaming_activity,
    )

    # Sync slash commands with Discord API upon startup
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

    print(f"Logged in as {bot.user} (Python Bot Live & Streaming!)")


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
        # Load commands from 'cogs' directory if it exists
        if os.path.exists("cogs"):
            await load_commands("cogs")

        await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
