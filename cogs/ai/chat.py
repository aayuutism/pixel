import os
import re
import discord
from discord.ext import commands
from groq import AsyncGroq

# Initialize Async Groq Client
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT =  "You are Pixel, a casual, friendly, and concise Discord AI companion. Keep your responses to 1-2 short sentences using lowercase text and a warm, playful tone."

class ChatCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots (including herself)
        if message.author.bot:
            return

        # Check if the bot is mentioned
        is_mentioned = self.bot.user in message.mentions and not message.mention_everyone

        # Check if message is a reply to Pixel
        is_reply_to_bot = False
        if message.reference and message.reference.message_id:
            try:
                ref_msg = await message.channel.fetch_message(message.reference.message_id)
                if ref_msg and ref_msg.author.id == self.bot.user.id:
                    is_reply_to_bot = True
            except (discord.NotFound, discord.HTTPException):
                pass

        # Check if message is in DMs
        is_dm = isinstance(message.channel, discord.DMChannel)

        # Ignore message if none of the trigger conditions match
        if not is_mentioned and not is_reply_to_bot and not is_dm:
            return

        # Show typing indicator while generating response
        async with message.channel.typing():
            try:
                # Fetch recent messages for conversation context (memory)
                messages_context = []
                async for msg in message.channel.history(limit=10, oldest_first=True):
                    # Clean out bot mention tags from text
                    clean_content = re.sub(f"<@!?{self.bot.user.id}>", "", msg.content).strip()
                    if not clean_content:
                        continue

                    if msg.author.id == self.bot.user.id:
                        messages_context.append({"role": "assistant", "content": clean_content})
                    elif not msg.author.bot:
                        messages_context.append({"role": "user", "content": clean_content})

                # Fallback if context is empty
                if not messages_context:
                    messages_context.append({"role": "user", "content": "hi"})

                # Build final payload
                payload = [{"role": "system", "content": SYSTEM_PROMPT}] + messages_context

                # Send request to Groq API
                response = await groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=payload,
                )

                reply_text = response.choices[0].message.content

                if not reply_text:
                    return await message.reply("I've got nothing to say to that.")

                await message.reply(reply_text.strip())

            except Exception as e:
                print(f"Chat Error: {e}")
                await message.reply("Ah, my mind went blank for a second. What were we saying?")


async def setup(bot: commands.Bot):
    if not bot.get_cog("ChatCog"):
        await bot.add_cog(ChatCog(bot))
