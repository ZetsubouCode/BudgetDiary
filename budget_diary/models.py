from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class User:
    discord_id: int
    username: str
    pin_hash: str
    language: str = "en"
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "discord_id": self.discord_id,
            "username": self.username,
            "pin_hash": self.pin_hash,
            "language": self.language,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "User":
        return cls(
            discord_id=int(payload["discord_id"]),
            username=payload["username"],
            pin_hash=payload["pin_hash"],
            language=payload.get("language", "en"),
            email=payload.get("email"),
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
        )


@dataclass
class Category:
    name: str
    category_type: str
    emoji: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category_type": self.category_type,
            "emoji": self.emoji,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Category":
        return cls(
            name=payload["name"],
            category_type=payload["category_type"],
            emoji=payload.get("emoji"),
            created_at=datetime.fromisoformat(payload["created_at"]),
        )


@dataclass
class Transaction:
    amount: float
    category: str
    category_type: str
    note: Optional[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": self.amount,
            "category": self.category,
            "category_type": self.category_type,
            "note": self.note,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Transaction":
        return cls(
            amount=float(payload["amount"]),
            category=payload["category"],
            category_type=payload["category_type"],
            note=payload.get("note"),
            created_at=datetime.fromisoformat(payload["created_at"]),
        )


def ensure_category_type(category_type: str) -> str:
    normalized = category_type.lower()
    if normalized not in {"income", "outcome"}:
        raise ValueError("category_type must be 'income' or 'outcome'")
    return normalized


def calculate_balance(transactions: List[Transaction]) -> float:
    balance = 0.0
    for txn in transactions:
        if txn.category_type == "income":
            balance += txn.amount
        else:
            balance -= txn.amount
    return balance
