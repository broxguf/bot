import aiosqlite

DB_NAME = "tokens.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS alerted_tokens (
                token TEXT PRIMARY KEY
            )
            '''
        )
        await db.commit()

async def already_alerted(token):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT token FROM alerted_tokens WHERE token=?",
            (token,)
        )
        row = await cursor.fetchone()
        return row is not None

async def save_alerted(token):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO alerted_tokens(token) VALUES(?)",
            (token,)
        )
        await db.commit()
