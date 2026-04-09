import asyncio
from app.core.database import init_db
from app.bots.driver_bot import start_driver_bot
from app.bots.passenger_bot import start_passenger_bot

async def main():
    await init_db()
    # Запуск ботов параллельно
    await asyncio.gather(
        start_driver_bot(),
        start_passenger_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())
