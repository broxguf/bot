import aiohttp
import asyncio
from datetime import datetime, timezone

from filters import is_valid_token
from alerts import send_alert
from database import already_alerted, save_alerted
from logger import logger
from config import BIRDEYE_API_KEY

BIRDEYE_URL = "https://public-api.birdeye.so/defi/tokenlist?sort_by=v24hUSD&sort_type=desc"

headers = {
    "X-API-KEY": BIRDEYE_API_KEY
}

async def fetch_tokens():

    async with aiohttp.ClientSession() as session:

        async with session.get(BIRDEYE_URL, headers=headers) as response:

            data = await response.json()

            return data.get("data", {}).get("tokens", [])

async def scanner_loop():

    while True:

        try:

            tokens = await fetch_tokens()

            for token in tokens:

                try:

                    created_at = token.get("createdAt")

                    if created_at:
                        created_dt = datetime.fromtimestamp(
                            created_at,
                            tz=timezone.utc
                        )

                        age_days = (
                            datetime.now(timezone.utc) - created_dt
                        ).days
                    else:
                        age_days = 999

                    token_data = {
                        "symbol": token.get("symbol", "UNKNOWN"),
                        "address": token.get("address"),
                        "priceChange": float(token.get("priceChange24hPercent", 0)),
                        "volume": float(token.get("v24hUSD", 0)),
                        "liquidity": float(token.get("liquidity", 0)),
                        "marketCap": float(token.get("mc", 0)),
                        "age_days": age_days
                    }

                    if not token_data["address"]:
                        continue

                    if await already_alerted(token_data["address"]):
                        continue

                    if is_valid_token(token_data):

                        logger.info(
                            f'PUMP DETECTED: {token_data["symbol"]}'
                        )

                        await send_alert(token_data)

                        await save_alerted(
                            token_data["address"]
                        )

                except Exception as e:
                    logger.error(e)

            await asyncio.sleep(60)

        except Exception as e:

            logger.error(e)

            await asyncio.sleep(30)
