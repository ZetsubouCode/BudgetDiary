from __future__ import annotations

import hashlib
from typing import Dict, Optional, Tuple

from bot.config import DEFAULT_LANGUAGE, DEFAULT_REGION
from bot.storage.json_store import JsonStore
from bot.utils.dates import now_iso
from util.logger import LoggerSingleton


class UserService:
    def __init__(self, store: JsonStore):
        self.store = store
        self.logger = LoggerSingleton.get_instance()

    @staticmethod
    def _hash_pin(pin: str) -> str:
        return hashlib.sha256(pin.encode()).hexdigest()

    async def register(
        self,
        discord_id: int | str,
        username: str,
        pin: str,
        language: str = DEFAULT_LANGUAGE,
        region: str = DEFAULT_REGION,
        email: Optional[str] = None,
    ) -> Tuple[bool, str]:
        user_id = str(discord_id)
        now = now_iso()

        def updater(data: Dict) -> Dict:
            if user_id in data:
                return data
            data[user_id] = {
                "discord_username": username,
                "email": email,
                "pin_hash": self._hash_pin(pin),
                "language": language or DEFAULT_LANGUAGE,
                "region": region or DEFAULT_REGION,
                "created_at": now,
                "updated_at": now,
            }
            return data

        data = await self.store.update(updater)
        if user_id in data and data[user_id]["created_at"] == now:
            message = f"User {username} registered with region {data[user_id]['region']}."
            self.logger.log(30, message)
            return True, message
        return False, f"User {username} is already registered."

    async def get_user(self, discord_id: int | str) -> Optional[Dict]:
        data = await self.store.read()
        return data.get(str(discord_id))

    async def ensure_user(self, discord_id: int | str, username: str) -> Dict:
        """Create a minimal user shell if missing (no PIN)."""
        user_id = str(discord_id)
        now = now_iso()

        def updater(data: Dict) -> Dict:
            if user_id not in data:
                data[user_id] = {
                    "discord_username": username,
                    "language": DEFAULT_LANGUAGE,
                    "region": DEFAULT_REGION,
                    "created_at": now,
                    "updated_at": now,
                }
            return data

        data = await self.store.update(updater)
        return data[user_id]

    async def verify_pin(self, discord_id: int | str, pin: str) -> bool:
        user = await self.get_user(discord_id)
        if not user or "pin_hash" not in user:
            return False
        return user["pin_hash"] == self._hash_pin(pin)

    async def update_region(self, discord_id: int | str, region: str) -> Tuple[bool, str]:
        user_id = str(discord_id)
        region_upper = region.upper()
        now = now_iso()

        def updater(data: Dict) -> Dict:
            if user_id not in data:
                return data
            data[user_id]["region"] = region_upper
            data[user_id]["updated_at"] = now
            return data

        data = await self.store.update(updater)
        if user_id in data and data[user_id].get("region") == region_upper:
            message = f"Region updated to {region_upper}."
            self.logger.log(35, message)
            return True, message
        return False, "User not found. Register first with /register."

    async def update_language(self, discord_id: int | str, language: str) -> Tuple[bool, str]:
        user_id = str(discord_id)
        now = now_iso()

        def updater(data: Dict) -> Dict:
            if user_id not in data:
                return data
            data[user_id]["language"] = language
            data[user_id]["updated_at"] = now
            return data

        data = await self.store.update(updater)
        if user_id in data and data[user_id].get("language") == language:
            message = f"Language updated to {language}."
            self.logger.log(35, message)
            return True, message
        return False, "User not found. Register first with /register."
