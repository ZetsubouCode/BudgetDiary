from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional, Tuple


def parse_date(value: str, *, fallback_today: bool = True) -> date:
    """Parse many date formats; optionally fall back to today."""
    formats = ("%d-%m-%Y", "%d%m%Y", "%Y-%m-%d")
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            continue
    if fallback_today:
        return date.today()
    raise ValueError(f"Invalid date: {value}")


def parse_month(value: Optional[str]) -> date:
    """Parse a month string, returning the first day of that month."""
    if not value:
        today = date.today()
        return date(today.year, today.month, 1)
    formats = ("%m-%Y", "%m%Y", "%Y-%m")
    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt).date()
            return date(parsed.year, parsed.month, 1)
        except (ValueError, TypeError):
            continue
    today = date.today()
    return date(today.year, today.month, 1)


def start_end_of_month(month_start: date) -> Tuple[date, date]:
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    return month_start, month_end


def start_end_of_year(year_value: int) -> Tuple[date, date]:
    start = date(year_value, 1, 1)
    end = date(year_value, 12, 31)
    return start, end


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def to_iso(value: date) -> str:
    return value.strftime("%Y-%m-%d")
