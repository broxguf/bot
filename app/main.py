import asyncio

from scanner import scanner_loop
from websocket_listener import websocket_loop
from database import init_db
from logger import logger


async def main():
    logger.info("STARTING PUMPFUN BOT")
    await init_db()

    # Запускаем оба цикла одновременно:
    #   scanner_loop     — полный скан каждые SCAN_INTERVAL секунд
    #   websocket_loop   — мгновенный триггер при активности pump.fun
    await asyncio.gather(
        scanner_loop(),
        websocket_loop(),
    )


if __name__ == "__main__":
    asyncio.run(main())
