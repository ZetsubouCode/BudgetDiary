from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Dict, List, Tuple

from bot.services.category_service import CategoryService
from bot.services.transaction_service import TransactionService
from bot.services.user_service import UserService
from bot.utils.currency import format_amount
from bot.utils.dates import start_end_of_month, start_end_of_year


class ReportService:
    def __init__(
        self,
        transaction_service: TransactionService,
        category_service: CategoryService,
        user_service: UserService,
    ):
        self.tx = transaction_service
        self.categories = category_service
        self.users = user_service

    async def _category_lookup(self, user_id: str) -> Dict:
        _, _, cats = await self.categories.list_categories(user_id, category_type=None, include_deleted=True)
        return cats

    def _category_label(self, category: Dict, language: str) -> str:
        if not category:
            return "Unknown"
        desc = category.get("description", {})
        return desc.get(language) or desc.get("en") or desc.get("id") or next(iter(desc.values()), "Unknown")

    async def income_report(self, discord_id: int | str, start: date, end: date, language: str, region: str) -> Dict:
        cats = await self._category_lookup(str(discord_id))
        incomes = await self.tx.incomes_between(discord_id, start, end)

        total = sum(item.get("amount", 0) for item in incomes)
        items = []
        for item in sorted(incomes, key=lambda r: r.get("date")):
            cat = cats.get("income", {}).get(item.get("category_id"), {})
            items.append(
                {
                    "category_name": self._category_label(cat, language),
                    "emoticon": cat.get("emoticon", ""),
                    "amount": item.get("amount", 0),
                    "description": item.get("description", ""),
                    "date": item.get("date", ""),
                }
            )

        return {"total": format_amount(total, region), "items": items}

    async def outcome_report(self, discord_id: int | str, start: date, end: date, language: str, region: str) -> Dict:
        cats = await self._category_lookup(str(discord_id))
        outcomes = await self.tx.outcomes_between(discord_id, start, end)

        total = sum(item.get("amount", 0) for item in outcomes)
        items = []
        for item in sorted(outcomes, key=lambda r: r.get("date")):
            cat = cats.get("outcome", {}).get(item.get("outcome_category_id"), {})
            income_cat = cats.get("income", {}).get(item.get("source_income_id"), {})
            items.append(
                {
                    "category_name": self._category_label(cat, language),
                    "income_source": self._category_label(income_cat, language),
                    "emoticon": cat.get("emoticon", ""),
                    "amount": item.get("amount", 0),
                    "description": item.get("description", ""),
                    "date": item.get("date", ""),
                }
            )

        return {"total": format_amount(total, region), "items": items}

    async def balances(self, discord_id: int | str, language: str, region: str) -> List[Dict]:
        cats = await self._category_lookup(str(discord_id))
        balances = await self.tx.balance_by_income(discord_id)
        results = []
        for cid, values in balances.items():
            cat = cats.get("income", {}).get(cid, {})
            results.append(
                {
                    "income_id": cid,
                    "name": self._category_label(cat, language),
                    "emoticon": cat.get("emoticon", ""),
                    "in": format_amount(values.get("in", 0), region),
                    "out": format_amount(values.get("out", 0), region),
                    "transfer_in": format_amount(values.get("transfer_in", 0), region),
                    "transfer_out": format_amount(values.get("transfer_out", 0), region),
                    "balance": format_amount(values.get("balance", 0), region),
                }
            )
        results.sort(key=lambda item: item.get("name"))
        return results

    async def top_outcome(self, discord_id: int | str, start: date, end: date, language: str, region: str) -> Dict:
        cats = await self._category_lookup(str(discord_id))
        largest, top_category = await self.tx.top_outcome(discord_id, start, end)
        result: Dict = {}

        if largest:
            cat = cats.get("outcome", {}).get(largest.get("outcome_category_id"), {})
            result["largest"] = {
                "category_name": self._category_label(cat, language),
                "amount": format_amount(largest.get("amount", 0), region),
                "description": largest.get("description", ""),
                "date": largest.get("date", ""),
            }

        if top_category:
            cat_id, amount = top_category
            cat = cats.get("outcome", {}).get(cat_id, {})
            result["top_category"] = {
                "category_name": self._category_label(cat, language),
                "amount": format_amount(amount, region),
            }
        return result

    async def monthly_curation(self, discord_id: int | str, month_start: date, language: str, region: str) -> Dict:
        cats = await self._category_lookup(str(discord_id))
        start, end = start_end_of_month(month_start)
        tx = await self.tx.monthly_curation(discord_id, start, end)

        incomes_grouped: Dict[str, float] = defaultdict(float)
        for item in tx["incomes"]:
            cat = cats.get("income", {}).get(item.get("category_id"), {})
            name = self._category_label(cat, language)
            incomes_grouped[name] += float(item.get("amount", 0))

        outcomes_grouped: Dict[str, float] = defaultdict(float)
        for item in tx["outcomes"]:
            cat = cats.get("outcome", {}).get(item.get("outcome_category_id"), {})
            name = self._category_label(cat, language)
            outcomes_grouped[name] += float(item.get("amount", 0))

        balance_view = []
        for cid, values in tx["balance"].items():
            cat = cats.get("income", {}).get(cid, {})
            balance_view.append(
                {
                    "income_id": cid,
                    "name": self._category_label(cat, language),
                    "balance": format_amount(values.get("balance", 0), region),
                }
            )

        return {
            "incomes": {name: format_amount(amount, region) for name, amount in incomes_grouped.items()},
            "outcomes": {name: format_amount(amount, region) for name, amount in outcomes_grouped.items()},
            "balances": balance_view,
        }

    async def yearly_outcome_summary(self, discord_id: int | str, year: int, language: str, region: str) -> Dict:
        start, end = start_end_of_year(year)
        return await self.outcome_report(discord_id, start, end, language, region)
