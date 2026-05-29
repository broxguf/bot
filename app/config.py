from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

PRICE_PUMP_PERCENT = float(os.getenv("PRICE_PUMP_PERCENT", 25))
MIN_VOLUME = float(os.getenv("MIN_VOLUME", 5000))
MIN_LIQUIDITY = float(os.getenv("MIN_LIQUIDITY", 5000))
