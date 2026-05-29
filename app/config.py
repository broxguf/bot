import os
import sys

# Сначала читаем settings.py, потом переменные окружения их перезаписывают.
# Так работает и локальный запуск (через settings.py) и Docker (через env vars).
from settings import (
    BOT_TOKEN        as _BOT_TOKEN,
    CHAT_ID          as _CHAT_ID,
    HELIUS_API_KEY   as _HELIUS_API_KEY,
    PRICE_PUMP_PERCENT,
    MIN_VOLUME,
    MIN_LIQUIDITY,
    MIN_AGE_DAYS,
    SCAN_INTERVAL,
    WS_SCAN_COOLDOWN,
)

BOT_TOKEN      = os.getenv("BOT_TOKEN")      or _BOT_TOKEN
CHAT_ID        = os.getenv("CHAT_ID")        or _CHAT_ID
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY") or _HELIUS_API_KEY

PRICE_PUMP_PERCENT = float(os.getenv("PRICE_PUMP_PERCENT", PRICE_PUMP_PERCENT))
MIN_VOLUME         = float(os.getenv("MIN_VOLUME",         MIN_VOLUME))
MIN_LIQUIDITY      = float(os.getenv("MIN_LIQUIDITY",      MIN_LIQUIDITY))
MIN_AGE_DAYS       = int(os.getenv("MIN_AGE_DAYS",         MIN_AGE_DAYS))
SCAN_INTERVAL      = int(os.getenv("SCAN_INTERVAL",        SCAN_INTERVAL))
WS_SCAN_COOLDOWN   = int(os.getenv("WS_SCAN_COOLDOWN",     WS_SCAN_COOLDOWN))

# Проверка обязательных переменных
_required = {"BOT_TOKEN": BOT_TOKEN, "CHAT_ID": CHAT_ID, "HELIUS_API_KEY": HELIUS_API_KEY}
_missing  = [k for k, v in _required.items() if not v]
if _missing:
    print(f"ERROR: Не заданы обязательные переменные: {', '.join(_missing)}", flush=True)
    print("Заполни их в app/settings.py или задай как переменные окружения.", flush=True)
    sys.exit(1)
