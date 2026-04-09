import asyncio
import logging
from app.core.database import create_pool, init_db

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    logging.info("Боты запущены")

if __name__ == "__main__":
    asyncio.run(main())
