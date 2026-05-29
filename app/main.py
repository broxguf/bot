import asyncio

from scanner import scanner_loop
from database import init_db
from logger import logger


async def main():
    logger.info("STARTING PUMPFUN BOT")
    await init_db()
    await scanner_loop()


if __name__ == "__main__":
    asyncio.run(main())
