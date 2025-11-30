from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Dict, Optional

from budget_diary.config import settings
from budget_diary.models import User, calculate_balance
from budget_diary.storage.json_store import JsonStore


class UserService:
    def __init__(self) -> None:
        self.store = JsonStore(settings.users_file, default_factory=dict)
        self.transaction_store = JsonStore(settings.transactions_file, default_factory=dict)

    @staticmethod
    def hash_pin(pin: str) -> str:
        return hashlib.sha256(pin.encode()).hexdigest()

    def register_user(self, discord_id: int, username: str, pin: str, *, language: str, email: Optional[str] = None) -> tuple[bool, str]:
        def mutator(payload: Dict[str, Dict]) -> Dict[str, Dict]:
            if str(discord_id) in payload:
                raise ValueError("User already registered")

            now = datetime.utcnow().isoformat()
            payload[str(discord_id)] = User(
                discord_id=discord_id,
                username=username,
                pin_hash=self.hash_pin(pin),
                language=language,
                email=email,
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now),
            ).to_dict()
            return payload

        try:
            self.store.update(mutator)
            return True, "User registered successfully"
        except ValueError as exc:
            return False, str(exc)

    def get_user(self, discord_id: int) -> Optional[User]:
        payload = self.store.read()
        if str(discord_id) not in payload:
            return None
        return User.from_dict(payload[str(discord_id)])

    def verify_pin(self, discord_id: int, pin: str) -> bool:
        user = self.get_user(discord_id)
        if not user:
            return False
        return user.pin_hash == self.hash_pin(pin)

    def summary(self, discord_id: int) -> Optional[Dict[str, str]]:
        user = self.get_user(discord_id)
        if not user:
            return None

        transactions_payload = self.transaction_store.read().get(str(discord_id), [])
        balance = calculate_balance([UserService._transaction_from_dict(entry) for entry in transactions_payload])
        return {
            "username": user.username,
            "language": user.language,
            "email": user.email or "-",
            "created_at": user.created_at.strftime("%Y-%m-%d"),
            "balance": f"{balance:,.2f}",
        }

    @staticmethod
    def _transaction_from_dict(payload: Dict) -> "Transaction":
        from budget_diary.models import Transaction

        return Transaction.from_dict(payload)
