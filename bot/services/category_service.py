from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from bot.config import CATEGORY_TEMPLATE_FILE, DEFAULT_LANGUAGE
from bot.storage.json_store import JsonStore
from util.logger import LoggerSingleton


class CategoryService:
    def __init__(self, store: JsonStore):
        self.store = store
        self.logger = LoggerSingleton.get_instance()

    async def ensure_user_categories(self, discord_id: int | str, *, use_template: bool = True) -> Dict:
        user_id = str(discord_id)

        def updater(data: Dict) -> Dict:
            if user_id not in data:
                data[user_id] = {"income": {}, "outcome": {}, "counters": {"income": 0, "outcome": 0}}
                if use_template and CATEGORY_TEMPLATE_FILE.exists():
                    try:
                        template = json.loads(Path(CATEGORY_TEMPLATE_FILE).read_text(encoding="utf-8"))
                        data[user_id]["income"] = self._convert_template(template.get("income", []))
                        data[user_id]["outcome"] = self._convert_template(template.get("outcome", []))
                        data[user_id]["counters"] = {
                            "income": len(data[user_id]["income"]),
                            "outcome": len(data[user_id]["outcome"]),
                        }
                    except Exception as exc:  # best-effort template load
                        self.logger.log(25, f"Template load failed: {exc}")
            return data

        data = await self.store.update(updater)
        return data[user_id]

    def _convert_template(self, template_items):
        converted = {}
        for item in template_items:
            idx = str(item.get("id") or len(converted) + 1)
            description = item.get("description", {})
            normalized = {k.lower(): v for k, v in description.items()}
            converted[idx] = {
                "description": normalized,
                "emoticon": item.get("emoticon") or "",
                "is_deleted": False,
            }
        return converted

    async def list_categories(
        self,
        discord_id: int | str,
        category_type: Optional[str] = None,
        include_deleted: bool = False,
        raw_data: bool = False,
    ) -> Tuple[bool, str, Dict]:
        user_data = await self.ensure_user_categories(discord_id)
        if category_type:
            cats = {
                cid: c
                for cid, c in user_data.get(category_type, {}).items()
                if include_deleted or not c.get("is_deleted")
            }
            return True, "Fetched categories", cats if raw_data else {category_type: cats}

        categories = {}
        for cat_type in ("income", "outcome"):
            categories[cat_type] = {
                cid: c for cid, c in user_data.get(cat_type, {}).items() if include_deleted or not c.get("is_deleted")
            }
        return True, "Fetched categories", categories

    async def add_category(
        self, discord_id: int | str, category_type: str, name: str, emoticon: str = "", language: str = DEFAULT_LANGUAGE
    ) -> Tuple[bool, str, Optional[str]]:
        user_id = str(discord_id)
        category_type = category_type.lower()

        def updater(data: Dict) -> Dict:
            user_cats = data.setdefault(user_id, {"income": {}, "outcome": {}, "counters": {"income": 0, "outcome": 0}})
            counter_key = user_cats.setdefault("counters", {}).setdefault(category_type, 0)
            new_idx = str(counter_key + 1)
            user_cats["counters"][category_type] = counter_key + 1
            user_cats.setdefault(category_type, {})
            user_cats[category_type][new_idx] = {
                "description": {language.lower(): name},
                "emoticon": emoticon or "",
                "is_deleted": False,
            }
            data[user_id] = user_cats
            return data

        data = await self.store.update(updater)
        new_id = str(data[user_id]["counters"][category_type])
        message = f"Added {category_type} category '{name}'."
        self.logger.log(40, message)
        return True, message, new_id

    async def edit_category(
        self,
        discord_id: int | str,
        category_type: str,
        category_id: str,
        name: Optional[str],
        emoticon: Optional[str],
        language: str = DEFAULT_LANGUAGE,
    ) -> Tuple[bool, str, Optional[Dict]]:
        user_id = str(discord_id)
        category_type = category_type.lower()

        def updater(data: Dict) -> Dict:
            user_cats = data.get(user_id)
            if not user_cats or category_id not in user_cats.get(category_type, {}):
                return data
            target = user_cats[category_type][category_id]
            if name:
                target.setdefault("description", {})[language.lower()] = name
            if emoticon is not None:
                target["emoticon"] = emoticon
            user_cats[category_type][category_id] = target
            data[user_id] = user_cats
            return data

        data = await self.store.update(updater)
        user_cats = data.get(user_id, {})
        updated = user_cats.get(category_type, {}).get(category_id)
        if not updated:
            return False, "Category not found.", None
        return True, f"Updated {category_type} category.", updated

    async def delete_category(
        self, discord_id: int | str, category_type: str, category_id: str
    ) -> Tuple[bool, str]:
        user_id = str(discord_id)
        category_type = category_type.lower()

        def updater(data: Dict) -> Dict:
            user_cats = data.get(user_id)
            if not user_cats or category_id not in user_cats.get(category_type, {}):
                return data
            user_cats[category_type][category_id]["is_deleted"] = True
            data[user_id] = user_cats
            return data

        data = await self.store.update(updater)
        if category_id in data.get(user_id, {}).get(category_type, {}):
            return True, "Category deleted."
        return False, "Category not found."
