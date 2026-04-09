import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN_PASSENGER = os.getenv("BOT_TOKEN_PASSENGER")
BOT_TOKEN_DRIVER = os.getenv("BOT_TOKEN_DRIVER")

DATABASE_URL = os.getenv("DATABASE_URL")

GROUP_ID_PASSENGER = int(os.getenv("GROUP_ID_PASSENGER"))
GROUP_ID_DRIVER = int(os.getenv("GROUP_ID_DRIVER"))
