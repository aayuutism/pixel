import hashlib
import io
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


class ShipCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def calculate_love(self, id1: int, id2: int) -> int:
        """Deterministically generates a score (0-100) for a user pair."""
        sorted_ids = sorted([id1, id2])
        combined = f"{sorted_ids[0]}-{sorted_ids[1]}"
        return int(hashlib.sha256(combined.encode()).hexdigest(), 16) % 101

    async def fetch_image(
        self, session: aiohttp.ClientSession, url: str
    ) -> Image.Image:
        async with session.get(url) as resp:
            data = await resp.read()
            return Image.open(io.BytesIO(data)).convert("RGBA")

    def make_circle(self, img: Image.Image, size: int) -> Image.Image:
        """Crops image into a clean circle."""
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        output.paste(img, (0, 0), mask)
        return output

    def get_emoji_url(self, score: int) -> str:
        """Fetches high-res Apple 3D emojis directly to avoid missing font issues on Linux."""
        if score >= 90:
            # Pink Heart 🩷
            return "https://em-content.zobj.net/source/apple/354/pink-heart_1f977.png"
        elif score >= 50:
            # Heart Eyes 😍
            return "https://em-content.zobj.net/source/apple/354/smiling-face-with-heart-eyes_1f60d.png"
        elif score >= 20:
            # Broken Heart 💔
            return "https://em-content.zobj.net/source/apple/354/broken-heart_1f494.png"
        else:
            # Skull ☠️
            return "https://em-content.zobj.net/source/apple/354/skull-and-crossbones_2620-fe0f.png"

    async def generate_ship_image(
        self, user1: discord.User, user2: discord.User, score: int
    ) -> io.BytesIO:
        width, height = 700, 360
        canvas = Image.new("RGBA", (width, height), (24, 25, 28, 255))
        draw = ImageDraw.Draw(canvas)

        async with aiohttp.ClientSession() as session:
            avatar1_img = await self.fetch_image(
                session, user1.display_avatar.with_format("png").url
            )
            avatar2_img = await self.fetch_image(
                session, user2.display_avatar.with_format("png").url
            )
            emoji_img = await self.fetch_image(session, self.get_emoji_url(score))

        # Size and position avatars and middle emoji
        avatar_size = 170
        emoji_size = 140

        circ1 = self.make_circle(avatar1_img, avatar_size)
        circ2 = self.make_circle(avatar2_img, avatar_size)
        emoji_resized = emoji_img.resize((emoji_size, emoji_size), Image.Resampling.LANCZOS)

        canvas.paste(circ1, (75, 55), circ1)
        canvas.paste(emoji_resized, (280, 70), emoji_resized)
        canvas.paste(circ2, (455, 55), circ2)

        # Progress Bar Layout
        bar_x, bar_y = 110, 265
        bar_w, bar_h = 480, 48

        # Dark grey background bar
        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
            radius=6,
            fill=(112, 112, 112, 255),
        )

        # Light lavender-blue progress bar
        fill_w = int(bar_w * (score / 100))
        if fill_w > 0:
            draw.rounded_rectangle(
                [bar_x, bar_y, bar_x + fill_w, bar_y + bar_h],
                radius=6,
                fill=(211, 216, 253, 255),
            )

        # Bigger & Bolder Text
        try:
            font_text = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        except OSError:
            try:
                font_text = ImageFont.truetype("arial.ttf", 28)
            except OSError:
                font_text = ImageFont.load_default()

        draw.text(
            (bar_x + bar_w // 2, bar_y + bar_h // 2 - 1),
            f"{score}% love",
            fill=(38, 38, 38, 255),
            anchor="mm",
            font=font_text,
        )

        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    @app_commands.command(
        name="ship", description="Calculate love compatibility between two users."
    )
    @app_commands.describe(target="The user to ship with (optional)")
    @app_commands.allowed_contexts(
        guilds=True, dms=True, private_channels=True
    )
    async def ship(
        self,
        interaction: discord.Interaction,
        target: discord.User | None = None,
    ):
        await interaction.response.defer()

        target1 = interaction.user
        target2 = target or interaction.user

        score = self.calculate_love(target1.id, target2.id)

        name1 = target1.display_name
        name2 = target2.display_name
        ship_name = f"{name1[:len(name1)//2]}{name2[len(name2)//2:]} 💕"

        image_buffer = await self.generate_ship_image(target1, target2, score)
        file = discord.File(fp=image_buffer, filename="ship.png")

        embed = discord.Embed(
            title=ship_name, color=discord.Color.from_str("#2B2D31")
        )
        embed.set_image(url="attachment://ship.png")

        await interaction.followup.send(embed=embed, file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(ShipCog(bot))
