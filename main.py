import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from threading import Thread

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Bot Client with required intents
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.dm_messages = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)


# Helper function to recursively load command files (Cogs) safely
async def load_commands(directory: str):
    for root, _, files in os.walk(directory):
        for file in files:
            # Skip non-cog helper files like database.py or views.py
            if file.endswith(".py") and not file.startswith("_") and file not in ["database.py", "views.py"]:
                rel_path = os.path.relpath(os.path.join(root, file), start=".")
                module_name = rel_path[:-3].replace(os.sep, ".")
                try:
                    await bot.load_extension(module_name)
                    print(f"Loaded extension: {module_name}", flush=True)
                except commands.ExtensionAlreadyLoaded:
                    print(f"Skipped duplicate extension: {module_name}", flush=True)
                except Exception as e:
                    print(f"Failed to load extension {module_name}: {e}", flush=True)


@bot.event
async def on_ready():
    print(">>> ON_READY EVENT FIRED! <<<", flush=True)

    # --- STREAMING PRESENCE ---
    try:
        streaming_activity = discord.Streaming(
            name="Nothing suspicious going on here :3",
            url="https://www.youtube.com/watch?v=QDia3e12czc",
        )

        await bot.change_presence(
            status=discord.Status.online,
            activity=streaming_activity,
        )
        print(">>> PRESENCE SET TO STREAMING <<<", flush=True)
    except Exception as e:
        print(f"Failed to set presence: {e}", flush=True)

    # Sync slash commands with Discord API upon startup
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).", flush=True)
    except Exception as e:
        print(f"Failed to sync slash commands: {e}", flush=True)

    print(f"Logged in as {bot.user} (Python Bot Live & Streaming!)", flush=True)


# Global Slash Command Error Handler to see exact errors in Render logs
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    print(f"[SLASH COMMAND ERROR] Command '{interaction.command.name if interaction.command else 'Unknown'}': {error}", flush=True)
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ An internal error occurred while executing this command.", ephemeral=True)
        else:
            await interaction.followup.send("❌ An internal error occurred while executing this command.", ephemeral=True)
    except Exception:
        pass


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
    if os.path.exists("cogs"):
        await load_commands("cogs")

    try:
        print("Connecting to Discord...", flush=True)
        await bot.start(os.getenv("DISCORD_TOKEN"))
    except discord.HTTPException as e:
        if e.status == 429:
            print("Hit 429 Cloudflare IP rate limit. Exiting cleanly to allow restart...", flush=True)
            await bot.close()
            os._exit(1)
        else:
            await bot.close()
            raise e


if __name__ == "__main__":
    asyncio.run(main())
