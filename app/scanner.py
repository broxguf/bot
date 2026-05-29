import aiohttp
import asyncio
from datetime import datetime, timezone

from filters import is_valid_token
from alerts import send_alert
from database import already_alerted, save_alerted
from logger import logger
from config import SCAN_INTERVAL

# DexScreener — бесплатный API, ключ не нужен.
# Ищем именно pump.fun пары на Solana.
DEXSCREENER_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search?q=pump"

# Допустимые значения dexId для pump.fun в ответе DexScreener
PUMPFUN_DEX_IDS = {"pump.fun", "pumpfun", "pump_fun"}


async def fetch_pumpfun_pairs() -> list[dict]:
    headers = {"accept": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.get(DEXSCREENER_SEARCH_URL, headers=headers) as resp:
            if resp.status != 200:
                logger.error(f"DexScreener вернул HTTP {resp.status}")
                return []

            data = await resp.json()
            all_pairs = data.get("pairs") or []

    # Строгий фильтр: только Solana + только pump.fun
    pumpfun_pairs = [
        p for p in all_pairs
        if p.get("chainId") == "solana"
        and (
            p.get("dexId", "").lower() in PUMPFUN_DEX_IDS
            or "pump.fun" in (p.get("url") or "").lower()
        )
    ]

    logger.info(
        f"DexScreener: всего пар={len(all_pairs)}, "
        f"pump.fun/Solana={len(pumpfun_pairs)}"
    )
    return pumpfun_pairs


def parse_pair(pair: dict) -> dict | None:
    """Превращает пару DexScreener в нормализованный словарь токена."""
    base    = pair.get("baseToken") or {}
    address = base.get("address")

    if not address or not isinstance(address, str):
        return None

    # Возраст пары
    created_ms = pair.get("pairCreatedAt")
    if created_ms:
        created_dt = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc)
        age_days   = (datetime.now(timezone.utc) - created_dt).days
    else:
        age_days = 999  # неизвестный возраст — пропустится в фильтре

    price_change = (pair.get("priceChange") or {}).get("h24") or 0
    volume       = (pair.get("volume")      or {}).get("h24") or 0
    liquidity    = (pair.get("liquidity")   or {}).get("usd") or 0
    market_cap   = pair.get("marketCap") or pair.get("fdv") or 0

    return {
        "symbol":      base.get("symbol") or "UNKNOWN",
        "address":     address,
        "priceChange": float(price_change),
        "volume":      float(volume),
        "liquidity":   float(liquidity),
        "marketCap":   float(market_cap),
        "age_days":    age_days,
    }


async def scanner_loop():
    while True:
        try:
            pairs = await fetch_pumpfun_pairs()

            if not pairs:
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            for pair in pairs:
                try:
                    token = parse_pair(pair)
                    if token is None:
                        continue

                    if await already_alerted(token["address"]):
                        continue

                    if is_valid_token(token):
                        logger.info(f'PUMP DETECTED: {token["symbol"]} +{token["priceChange"]}%')
                        await send_alert(token)
                        await save_alerted(token["address"])

                except Exception as e:
                    logger.error(f"Ошибка обработки токена: {e}")

            await asyncio.sleep(SCAN_INTERVAL)

        except Exception as e:
            logger.error(f"Ошибка сканера: {e}")
            await asyncio.sleep(30)
