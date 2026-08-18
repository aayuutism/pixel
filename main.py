import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from threading import Thread

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Import the shared family_group
from cogs.family.groups import family_group

# Load environment variables
load_dotenv()

# Initialize Bot Client with required intents
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.dm_messages = True
intents.presences = True


class MyBot(commands.Bot):

    async def setup_hook(self):
        # 1. Register shared app command groups FIRST
        if not self.tree.get_command("family"):
            self.tree.add_command(family_group)

        # 2. Load all cogs next
        if os.path.exists("cogs"):
            await load_commands(self)

        # 3. Sync command tree AFTER all cogs and subcommands are attached
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash command(s).", flush=True)
        except Exception as e:
            print(f"Failed to sync slash commands: {e}", flush=True)


bot = MyBot(command_prefix="!", intents=intents)


# Helper function to recursively load command files (Cogs) safely
async def load_commands(bot_instance: commands.Bot):
    for root, _, files in os.walk("cogs"):
        for file in files:
            # Skip non-cog helper files
            if (
                file.endswith(".py")
                and not file.startswith("_")
                and file not in ["database.py", "views.py", "groups.py"]
            ):
                rel_path = os.path.relpath(os.path.join(root, file), start=".")
                module_name = rel_path[:-3].replace(os.sep, ".")
                try:
                    await bot_instance.load_extension(module_name)
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

    print(f"Logged in as {bot.user} (Python Bot Live & Streaming!)", flush=True)


# Global Slash Command Error Handler
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
