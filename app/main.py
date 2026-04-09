import asyncio
from app.core.logger import logging
from app.core.database import create_pool, init_db
from app.passenger.bot import create_passenger_bot
from app.driver.bot import create_driver_bot


async def main():
    await create_pool()
    await init_db()

    passenger_bot, passenger_dp = create_passenger_bot()
    driver_bot, driver_dp = create_driver_bot()

    await asyncio.gather(
        passenger_dp.start_polling(passenger_bot),
        driver_dp.start_polling(driver_bot)
    )


if __name__ == "__main__":
    logging.info("Боты запущены")
    asyncio.run(main())
