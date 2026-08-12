import os
import discord
from discord.ext import commands
from discord import app_commands
from openai import AsyncOpenAI

# Initialize xAI client using the OpenAI SDK structure
xai_client = AsyncOpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Renamed the command group to "ask"
    ask_group = app_commands.Group(name="ask", description="Ask AI commands")

    @ask_group.command(name="grok", description="Ask Grok a question!")
    @app_commands.describe(
        prompt="Your question for Grok",
        image="Optional image to include with your question"
    )
    async def grok(
        self, 
        interaction: discord.Interaction, 
        prompt: str, 
        image: discord.Attachment = None
    ):
        await interaction.response.send_message("••• **Grok** is thinking..")

        # Select model based on whether an image was attached
        model_name = "grok-2-vision-1212" if image else "grok-2-1212"

        if image and image.content_type and image.content_type.startswith("image/"):
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image.url}}
                ]
            }]
        else:
            messages = [{"role": "user", "content": prompt}]

        try:
            response = await xai_client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            reply_content = response.choices[0].message.content

            embed = discord.Embed(color=discord.Color.from_str("#8BB96E"))
            embed.title = prompt
            embed.description = reply_content
            embed.set_footer(
                text="xAI Grok • Results are AI generated", 
                icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png"
            )

            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"❌ An error occurred: `{str(e)}`")

async def setup(bot):
    await bot.add_cog(AICog(bot))
