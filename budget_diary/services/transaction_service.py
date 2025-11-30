from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from budget_diary.config import settings
from budget_diary.models import Transaction, calculate_balance, ensure_category_type
from budget_diary.storage.json_store import JsonStore
from budget_diary.services.category_service import CategoryService


class TransactionService:
    def __init__(self) -> None:
        self.store = JsonStore(settings.transactions_file, default_factory=dict)
        self.category_service = CategoryService()

    def add_transaction(
        self,
        discord_id: int,
        amount: float,
        category_type: str,
        category: str,
        note: Optional[str] = None,
    ) -> tuple[bool, str]:
        normalized = ensure_category_type(category_type)
        available = self.category_service.list_categories(discord_id, normalized)[normalized]
        if not any(cat.name.lower() == category.lower() for cat in available):
            return False, f"Unknown {normalized} category: {category}"

        def mutator(payload: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
            transactions = payload.setdefault(str(discord_id), [])
            transactions.append(
                Transaction(
                    amount=amount,
                    category=category,
                    category_type=normalized,
                    note=note,
                    created_at=datetime.utcnow(),
                ).to_dict()
            )
            payload[str(discord_id)] = transactions
            return payload

        self.store.update(mutator)
        return True, "Transaction recorded"

    def recent_transactions(self, discord_id: int, limit: int = 5) -> List[Transaction]:
        payload = self.store.read().get(str(discord_id), [])
        return [Transaction.from_dict(entry) for entry in sorted(payload, key=lambda x: x["created_at"], reverse=True)[:limit]]

    def balance(self, discord_id: int) -> float:
        payload = self.store.read().get(str(discord_id), [])
        return calculate_balance([Transaction.from_dict(entry) for entry in payload])
