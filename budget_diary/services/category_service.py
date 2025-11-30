from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from budget_diary.config import settings
from budget_diary.models import Category, ensure_category_type
from budget_diary.storage.json_store import JsonStore


class CategoryService:
    def __init__(self) -> None:
        self.store = JsonStore(settings.categories_file, default_factory=dict)
        self.template_store = JsonStore(settings.category_template_file, default_factory=self._default_template)

    def list_categories(self, discord_id: int, category_type: str | None = None) -> Dict[str, List[Category]]:
        payload = self._ensure_user_categories(discord_id)
        result: Dict[str, List[Category]] = {}

        types = [category_type] if category_type else ["income", "outcome"]
        for type_name in types:
            normalized = ensure_category_type(type_name)
            result[normalized] = [Category.from_dict(item) for item in payload.get(str(discord_id), {}).get(normalized, [])]
        return result

    def add_category(self, discord_id: int, name: str, category_type: str, emoji: str | None = None) -> tuple[bool, str]:
        normalized = ensure_category_type(category_type)

        def mutator(payload: Dict[str, Dict]) -> Dict[str, Dict]:
            user_categories = payload.setdefault(str(discord_id), self._user_template())
            if any(entry["name"].lower() == name.lower() for entry in user_categories[normalized]):
                raise ValueError("Category already exists")
            user_categories[normalized].append(Category(name=name, category_type=normalized, emoji=emoji).to_dict())
            payload[str(discord_id)] = user_categories
            return payload

        try:
            self.store.update(mutator)
            return True, f"Added {name} to {normalized} categories"
        except ValueError as exc:
            return False, str(exc)

    def _ensure_user_categories(self, discord_id: int) -> Dict[str, Dict]:
        payload = self.store.read()
        if str(discord_id) not in payload:
            payload[str(discord_id)] = self._user_template()
            self.store.write(payload)
        return payload

    def _user_template(self) -> Dict[str, List[Dict]]:
        template = self.template_store.read()
        return {
            "income": list(template.get("income", [])),
            "outcome": list(template.get("outcome", [])),
        }

    @staticmethod
    def _default_template() -> Dict[str, List[Dict]]:
        base_template = {
            "income": [
                {"name": "Salary", "category_type": "income", "emoji": "💼"},
                {"name": "Interest", "category_type": "income", "emoji": "🏦"},
            ],
            "outcome": [
                {"name": "Food", "category_type": "outcome", "emoji": "🍜"},
                {"name": "Bills", "category_type": "outcome", "emoji": "💡"},
                {"name": "Transport", "category_type": "outcome", "emoji": "🚌"},
            ],
        }
        return base_template
