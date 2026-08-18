import aiosqlite

DB_NAME = "family.db"

async def init_db():
    """Initializes the database tables if they do not exist."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Table for marriages/partnerships
        await db.execute("""
            CREATE TABLE IF NOT EXISTS marriages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                guild_id INTEGER DEFAULT 0
            )
        """)

        # Table for parent-child adoptions
        await db.execute("""
            CREATE TABLE IF NOT EXISTS adoptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                guild_id INTEGER DEFAULT 0
            )
        """)

        # Table for guild specific settings
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                guild_specific_families INTEGER DEFAULT 0
            )
        """)

        await db.commit()


async def get_guild_setting(guild_id: int) -> bool:
    """Returns True if guild-specific families are enabled, False if global."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT guild_specific_families FROM guild_settings WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return bool(row[0]) if row else False

async def add_marriage(user1_id: int, user2_id: int, guild_id: int = 0):
    """Creates a marriage/partnership between two users."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO marriages (user1_id, user2_id, guild_id) VALUES (?, ?, ?)",
            (user1_id, user2_id, guild_id)
        )
        await db.commit()

async def remove_marriage(user1_id: int, user2_id: int, guild_id: int = 0):
    """Removes a marriage/partnership between two users."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """DELETE FROM marriages 
               WHERE ((user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?))
               AND guild_id = ?""",
            (user1_id, user2_id, user2_id, user1_id, guild_id)
        )
        await db.commit()

async def add_adoption(parent_id: int, child_id: int, guild_id: int = 0):
    """Adds a parent-child relationship."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO adoptions (parent_id, child_id, guild_id) VALUES (?, ?, ?)",
            (parent_id, child_id, guild_id)
        )
        await db.commit()

async def remove_adoption(parent_id: int, child_id: int, guild_id: int = 0):
    """Removes a parent-child relationship."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM adoptions WHERE parent_id = ? AND child_id = ? AND guild_id = ?",
            (parent_id, child_id, guild_id)
        )
        await db.commit()
