import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Set up basic bot intents
intents = discord.Intents.default()
intents.message_content = True


class MyBot(commands.Bot):

    async def setup_hook(self):
        # Automatically load every extension/cog inside the cogs folder
        # Discord.py will automatically detect and register the commands 
        # inside your cogs, even those using the groups imported from groups.py
        if os.path.exists("cogs"):
            for root, _, files in os.walk("cogs"):
                for file in files:
                    if file.endswith(".py") and not file.startswith("_"):
                        rel_path = os.path.relpath(os.path.join(root, file), start=".")
                        cog_name = rel_path[:-3].replace(os.sep, ".")
                        
                        try:
                            await self.load_extension(cog_name)
                            print(f"Loaded cog: {cog_name}")
                        except Exception as e:
                            print(f"Oops, failed to load {cog_name}: {e}")

        # Sync the command tree with Discord
        # Run this once with the line below, then you can comment/remove it
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
        print("All slash commands synced with Discord!")


# Initialize the bot instance
bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    # Set a nice streaming status when the bot boots up
    activity = discord.Streaming(
        name="Nothing suspicious going on here :3",
        url="https://www.youtube.com/watch?v=QDia3e12czc",
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"We're logged in as {bot.user} and ready to go!")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)

    error_message = "Welp, it's bitching. AGAIN."
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
