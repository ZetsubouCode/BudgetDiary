from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

from bot.config import DEFAULT_REGION, REGIONS


def normalize_region(region: str | None) -> str:
    if not region:
        return DEFAULT_REGION
    region_upper = region.upper()
    return region_upper if region_upper in REGIONS else DEFAULT_REGION


def format_amount(amount: float | int, region: str | None = None) -> str:
    normalized = normalize_region(region)
    cfg: Dict[str, str | int] = REGIONS.get(normalized, REGIONS[DEFAULT_REGION])
    precision = int(cfg.get("precision", 2))
    symbol = cfg.get("symbol", "")
    quantize_str = "1." + ("0" * precision)
    value = Decimal(str(amount)).quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
    formatted = f"{value:,.{precision}f}" if precision else f"{value:,}"
    return f"{symbol} {formatted}".strip()
