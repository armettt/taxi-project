import asyncpg
import os
import logging

DATABASE_URL = os.getenv("DATABASE_URL")
# Neon обычно создаёт схему с именем пользователя (не public)
DB_SCHEMA = os.getenv("DB_SCHEMA", "authenticator")  # <- поставь свой Neon username

pool: asyncpg.pool.Pool | None = None

async def create_pool() -> asyncpg.pool.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL)
        logging.info("✅ Database pool created")
    return pool

async def init_db():
    global pool
    if pool is None:
        await create_pool()

    async with pool.acquire() as conn:
        # Устанавливаем схему по умолчанию
        await conn.execute(f'SET search_path TO {DB_SCHEMA};')

        # Таблица заказов
        await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.orders (
            id SERIAL PRIMARY KEY,
            passenger_id BIGINT NOT NULL,
            driver_id BIGINT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # Таблица водителей
        await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.drivers (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            name TEXT,
            car TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # Таблица пассажиров
        await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.passengers (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
    logging.info("✅ Database initialized")
