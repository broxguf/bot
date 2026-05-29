from aiogram import Bot
from config import BOT_TOKEN, CHAT_ID

bot = Bot(token=BOT_TOKEN)

async def send_alert(data):

    text = f'''
🚀 PUMP DETECTED

TOKEN: {data["symbol"]}
Рост: +{data["priceChange"]}%
MCAP: ${data["marketCap"]}
Volume: ${data["volume"]}
Liquidity: ${data["liquidity"]}
Age: {data["age_days"]} days

Ссылка:
https://pump.fun/coin/{data["address"]}
'''

    await bot.send_message(CHAT_ID, text)
