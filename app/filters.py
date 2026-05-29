from config import PRICE_PUMP_PERCENT, MIN_VOLUME, MIN_LIQUIDITY, MIN_AGE_DAYS


def is_valid_token(data: dict) -> bool:
    price_change = data.get("priceChange", 0)
    volume       = data.get("volume",      0)
    liquidity    = data.get("liquidity",   0)
    age_days     = data.get("age_days",    0)

    # Только pump.fun — токены СТАРШЕ MIN_AGE_DAYS дней
    if age_days < MIN_AGE_DAYS:
        return False

    if price_change < PRICE_PUMP_PERCENT:
        return False

    if volume < MIN_VOLUME:
        return False

    if liquidity < MIN_LIQUIDITY:
        return False

    return True
