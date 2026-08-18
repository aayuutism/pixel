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
