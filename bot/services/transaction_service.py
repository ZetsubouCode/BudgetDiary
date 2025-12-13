from __future__ import annotations

from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Tuple

from bot.storage.json_store import JsonStore
from bot.utils.dates import now_iso, to_iso
from util.logger import LoggerSingleton


class TransactionService:
    def __init__(self, store: JsonStore):
        self.store = store
        self.logger = LoggerSingleton.get_instance()

    def _empty_user_struct(self) -> Dict:
        return {
            "incomes": {},
            "outcomes": {},
            "transfers": {},
            "counters": {"income": 0, "outcome": 0, "transfer": 0},
        }

    async def _ensure_user(self, user_id: str) -> Dict:
        def updater(data: Dict) -> Dict:
            data.setdefault(user_id, self._empty_user_struct())
            return data

        data = await self.store.update(updater)
        return data[user_id]

    async def add_income(
        self,
        discord_id: int | str,
        category_id: str,
        amount: float,
        description: str,
        when: date,
        region: str,
    ) -> Tuple[bool, str, Dict]:
        user_id = str(discord_id)
        await self._ensure_user(user_id)

        def updater(data: Dict) -> Dict:
            user_tx = data.get(user_id, self._empty_user_struct())
            counter = user_tx["counters"]["income"] + 1
            user_tx["counters"]["income"] = counter
            record_id = str(counter)
            user_tx["incomes"][record_id] = {
                "id": record_id,
                "category_id": category_id,
                "amount": float(amount),
                "description": description or "",
                "date": to_iso(when),
                "region": region,
                "created_at": now_iso(),
            }
            data[user_id] = user_tx
            return data

        data = await self.store.update(updater)
        record_id = str(data[user_id]["counters"]["income"])
        record = data[user_id]["incomes"][record_id]
        self.logger.log(35, f"Income {record_id} added for {user_id}.")
        return True, "Income saved.", record

    async def add_outcome(
        self,
        discord_id: int | str,
        outcome_category_id: str,
        income_source_id: str,
        amount: float,
        description: str,
        when: date,
        region: str,
    ) -> Tuple[bool, str, Dict]:
        user_id = str(discord_id)
        await self._ensure_user(user_id)

        def updater(data: Dict) -> Dict:
            user_tx = data.get(user_id, self._empty_user_struct())
            counter = user_tx["counters"]["outcome"] + 1
            user_tx["counters"]["outcome"] = counter
            record_id = str(counter)
            user_tx["outcomes"][record_id] = {
                "id": record_id,
                "outcome_category_id": outcome_category_id,
                "source_income_id": income_source_id,
                "amount": float(amount),
                "description": description or "",
                "date": to_iso(when),
                "region": region,
                "created_at": now_iso(),
            }
            data[user_id] = user_tx
            return data

        data = await self.store.update(updater)
        record_id = str(data[user_id]["counters"]["outcome"])
        record = data[user_id]["outcomes"][record_id]
        self.logger.log(35, f"Outcome {record_id} added for {user_id}.")
        return True, "Outcome saved.", record

    async def transfer_income(
        self, discord_id: int | str, source_income_id: str, destination_income_id: str, amount: float, note: str = ""
    ) -> Tuple[bool, str, Dict]:
        user_id = str(discord_id)
        await self._ensure_user(user_id)

        def updater(data: Dict) -> Dict:
            user_tx = data.get(user_id, self._empty_user_struct())
            counter = user_tx["counters"]["transfer"] + 1
            user_tx["counters"]["transfer"] = counter
            record_id = str(counter)
            user_tx["transfers"][record_id] = {
                "id": record_id,
                "from_income_id": source_income_id,
                "to_income_id": destination_income_id,
                "amount": float(amount),
                "note": note or "",
                "created_at": now_iso(),
            }
            data[user_id] = user_tx
            return data

        data = await self.store.update(updater)
        record_id = str(data[user_id]["counters"]["transfer"])
        record = data[user_id]["transfers"][record_id]
        self.logger.log(35, f"Transfer {record_id} added for {user_id}.")
        return True, "Transfer saved.", record

    async def delete_income(self, discord_id: int | str, record_id: str) -> Tuple[bool, str]:
        user_id = str(discord_id)

        def updater(data: Dict) -> Dict:
            user_tx = data.get(user_id)
            if not user_tx or record_id not in user_tx.get("incomes", {}):
                return data
            user_tx["incomes"].pop(record_id, None)
            data[user_id] = user_tx
            return data

        data = await self.store.update(updater)
        if record_id not in data.get(user_id, {}).get("incomes", {}):
            return True, "Income deleted."
        return False, "Income not found."

    async def delete_outcome(self, discord_id: int | str, record_id: str) -> Tuple[bool, str]:
        user_id = str(discord_id)

        def updater(data: Dict) -> Dict:
            user_tx = data.get(user_id)
            if not user_tx or record_id not in user_tx.get("outcomes", {}):
                return data
            user_tx["outcomes"].pop(record_id, None)
            data[user_id] = user_tx
            return data

        data = await self.store.update(updater)
        if record_id not in data.get(user_id, {}).get("outcomes", {}):
            return True, "Outcome deleted."
        return False, "Outcome not found."

    def _filter_by_date(self, records: Dict[str, Dict], start: date, end: date) -> List[Dict]:
        selected = []
        for record in records.values():
            try:
                record_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
            except Exception:
                continue
            if start <= record_date <= end:
                selected.append(record)
        return selected

    async def incomes_between(self, discord_id: int | str, start: date, end: date) -> List[Dict]:
        user_id = str(discord_id)
        data = await self._ensure_user(user_id)
        return self._filter_by_date(data.get("incomes", {}), start, end)

    async def outcomes_between(self, discord_id: int | str, start: date, end: date) -> List[Dict]:
        user_id = str(discord_id)
        data = await self._ensure_user(user_id)
        return self._filter_by_date(data.get("outcomes", {}), start, end)

    async def transfers(self, discord_id: int | str) -> List[Dict]:
        data = await self._ensure_user(str(discord_id))
        return list(data.get("transfers", {}).values())

    async def balance_by_income(self, discord_id: int | str) -> Dict[str, Dict[str, float]]:
        """Return per-income totals and balance."""
        user_id = str(discord_id)
        data = await self._ensure_user(user_id)
        totals: Dict[str, Dict[str, float]] = {}

        # sum incomes
        for income in data.get("incomes", {}).values():
            cid = income["category_id"]
            totals.setdefault(cid, {"in": 0.0, "out": 0.0, "transfer_in": 0.0, "transfer_out": 0.0})
            totals[cid]["in"] += float(income.get("amount", 0))

        # sum outcomes by source income
        for outcome in data.get("outcomes", {}).values():
            cid = outcome.get("source_income_id")
            if not cid:
                continue
            totals.setdefault(cid, {"in": 0.0, "out": 0.0, "transfer_in": 0.0, "transfer_out": 0.0})
            totals[cid]["out"] += float(outcome.get("amount", 0))

        # transfers
        for transfer in data.get("transfers", {}).values():
            src = transfer.get("from_income_id")
            dst = transfer.get("to_income_id")
            amt = float(transfer.get("amount", 0))
            if src:
                totals.setdefault(src, {"in": 0.0, "out": 0.0, "transfer_in": 0.0, "transfer_out": 0.0})
                totals[src]["transfer_out"] += amt
            if dst:
                totals.setdefault(dst, {"in": 0.0, "out": 0.0, "transfer_in": 0.0, "transfer_out": 0.0})
                totals[dst]["transfer_in"] += amt

        for cid, values in totals.items():
            inbound = values["in"] + values["transfer_in"]
            outbound = values["out"] + values["transfer_out"]
            values["balance"] = inbound - outbound
        return totals

    async def top_outcome(
        self, discord_id: int | str, start: date, end: date
    ) -> Tuple[Optional[Dict], Optional[Tuple[str, float]]]:
        """Return largest single outcome record and top category aggregate."""
        outcomes = await self.outcomes_between(discord_id, start, end)
        if not outcomes:
            return None, None
        largest = max(outcomes, key=lambda r: r.get("amount", 0))
        totals: Dict[str, float] = {}
        for record in outcomes:
            cid = record.get("outcome_category_id")
            totals[cid] = totals.get(cid, 0.0) + float(record.get("amount", 0))
        top_cat_id, top_amount = max(totals.items(), key=lambda item: item[1])
        return largest, (top_cat_id, top_amount)

    async def monthly_curation(self, discord_id: int | str, start: date, end: date) -> Dict:
        incomes = await self.incomes_between(discord_id, start, end)
        outcomes = await self.outcomes_between(discord_id, start, end)
        balance = await self.balance_by_income(discord_id)
        return {
            "incomes": incomes,
            "outcomes": outcomes,
            "balance": balance,
        }
