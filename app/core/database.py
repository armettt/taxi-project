import asyncpg
import os
import logging

DATABASE_URL = os.getenv("DATABASE_URL")
DB_SCHEMA = os.getenv("DB_SCHEMA", "authenticator")

pool: asyncpg.pool.Pool | None = None  # глобальная переменная для пула

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
        # Указываем схему пользователя
        await conn.execute(f'SET search_path TO {DB_SCHEMA};')

        # Таблица заказов
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            passenger_id BIGINT NOT NULL,
            driver_id BIGINT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # Таблица водителей
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            name TEXT,
            car TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # Таблица пассажиров
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
    logging.info("✅ Database initialized")
