from config import (
    PRICE_PUMP_PERCENT,
    MIN_VOLUME,
    MIN_LIQUIDITY
)

def is_valid_token(data):

    price_change = data.get("priceChange", 0)
    volume = data.get("volume", 0)
    liquidity = data.get("liquidity", 0)
    age_days = data.get("age_days", 999)

    # Монета должна быть СТАРШЕ 30 дней
    if age_days < 30:
        return False

    if price_change < PRICE_PUMP_PERCENT:
        return False

    if volume < MIN_VOLUME:
        return False

    if liquidity < MIN_LIQUIDITY:
        return False

    return True
