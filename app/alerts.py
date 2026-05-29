from aiogram import Bot
from config import BOT_TOKEN, CHAT_ID

bot = Bot(token=BOT_TOKEN)


async def send_alert(data: dict):
    text = (
        f"🚀 <b>PUMP DETECTED</b>\n\n"
        f"🪙 <b>TOKEN:</b> {data['symbol']}\n"
        f"📈 <b>Рост:</b> +{data['priceChange']:.1f}%\n"
        f"💰 <b>MCAP:</b> ${data['marketCap']:,.0f}\n"
        f"📊 <b>Volume 24h:</b> ${data['volume']:,.0f}\n"
        f"💧 <b>Liquidity:</b> ${data['liquidity']:,.0f}\n"
        f"📅 <b>Возраст:</b> {data['age_days']} дней\n\n"
        f"🔗 <a href='https://pump.fun/coin/{data['address']}'>pump.fun</a> | "
        f"<a href='https://dexscreener.com/solana/{data['address']}'>DexScreener</a>"
    )
    await bot.send_message(CHAT_ID, text, parse_mode="HTML")
