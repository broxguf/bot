"""
WebSocket-слушатель Helius.

Подписываемся на логи pump.fun программы в Solana.
При каждой новой транзакции (торг, создание токена) — сразу запускаем
скан DexScreener, не дожидаясь 60-секундного таймера в scanner_loop().

Оба цикла (scanner_loop + websocket_loop) работают одновременно:
  - websocket_loop  — быстрые сигналы, триггерит скан при активности
  - scanner_loop    — полный скан каждые SCAN_INTERVAL секунд (резерв)
"""

import asyncio
import json

import websockets

from config import HELIUS_API_KEY
from database import already_alerted, save_alerted
from filters import is_valid_token
from alerts import send_alert
from scanner import fetch_pumpfun_pairs, parse_pair
from logger import logger

# pump.fun bonding-curve программа на Solana
PUMPFUN_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

HELIUS_WS_URL = f"wss://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Минимальная пауза между WS-триггерными сканами (сек).
# Если транзакций много — не засыпаем DexScreener запросами.
WS_SCAN_COOLDOWN = 15


async def _scan_on_event():
    """Быстрый скан DexScreener, вызванный WS-событием."""
    try:
        pairs = await fetch_pumpfun_pairs()
        for pair in pairs:
            token = parse_pair(pair)
            if token is None:
                continue
            if await already_alerted(token["address"]):
                continue
            if is_valid_token(token):
                logger.info(
                    f'[WS] PUMP DETECTED: {token["symbol"]} '
                    f'+{token["priceChange"]:.1f}%'
                )
                await send_alert(token)
                await save_alerted(token["address"])
    except Exception as e:
        logger.error(f"[WS] Ошибка скана: {e}")


async def websocket_loop():
    """Основной цикл WebSocket — переподключается при обрыве."""
    last_scan_time: float = 0.0

    while True:
        try:
            logger.info("[WS] Подключение к Helius WebSocket...")
            async with websockets.connect(
                HELIUS_WS_URL,
                ping_interval=30,
                ping_timeout=20,
                open_timeout=15,
            ) as ws:

                # Подписываемся на логи, где упоминается pump.fun программа
                await ws.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [PUMPFUN_PROGRAM]},
                        {"commitment": "confirmed"},
                    ],
                }))

                sub_resp = await ws.recv()
                logger.info(f"[WS] Подписка: {sub_resp[:120]}")

                async for raw_msg in ws:
                    try:
                        msg = json.loads(raw_msg)
                    except Exception:
                        continue

                    # Пропускаем подтверждение подписки
                    if "result" in msg:
                        continue

                    # Получили уведомление о транзакции
                    now = asyncio.get_event_loop().time()
                    if now - last_scan_time < WS_SCAN_COOLDOWN:
                        continue  # слишком часто — пропускаем

                    last_scan_time = now
                    logger.info("[WS] Активность на pump.fun — запускаю скан")
                    asyncio.create_task(_scan_on_event())

        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"[WS] Соединение закрыто: {e}. Переподключение через 5с...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"[WS] Ошибка: {e}. Переподключение через 10с...")
            await asyncio.sleep(10)
