import asyncpg
from app.core.config import DATABASE_URL

pool = None


async def create_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)


async def get_pool():
    return pool


async def init_db():
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            phone TEXT
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            phone TEXT,
            brand TEXT,
            model TEXT,
            color TEXT,
            plate TEXT
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            client_id BIGINT,
            phone TEXT,
            username TEXT,
            from_loc TEXT,
            to_loc TEXT,
            comment TEXT,
            status TEXT DEFAULT 'waiting',
            driver_id BIGINT,
            message_id BIGINT
        );
        """)
