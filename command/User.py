import json, hashlib
from datetime import datetime, timedelta
from util.date_utils import Util
from util.logger import LoggerSingleton
from typing import Optional
from config.config import *

class User:
    logger = LoggerSingleton.get_instance()

    def _now_str() -> str:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _parse_minutes(value, default: int = 60) -> int:
        try:
            minutes = int(value)
        except (TypeError, ValueError):
            return default
        if minutes <= 0:
            return default
        return minutes

    def _parse_datetime(value: str):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    
    def hash_pin(pin: str) -> str:
        """
        Hash a PIN using SHA-256.
        
        Args:
            pin (str): The PIN to hash.
        
        Returns:
            str: The hashed PIN as a hexadecimal string.
        """
        return hashlib.sha256(pin.encode()).hexdigest()

    def verify_pin(pin: str, hashed_pin: str) -> bool:
        """
        Verify a PIN against a hashed PIN.
        
        Args:
            pin (str): The plain-text PIN to verify.
            hashed_pin (str): The hashed PIN to compare against.
        
        Returns:
            bool: True if the PIN matches the hash, False otherwise.
        """
        return User.hash_pin(pin) == hashed_pin
     
    def get_users(user_id:str=""):
        user_data = Util.read_json(JSON_USER_FILE_PATH)
        if not isinstance(user_data, dict):
            user_data = {}
        if user_id:
            return user_data.get(user_id, {})
        return user_data
    
    def get_user_language(discord_id:str):
        json_file = Util.read_json(JSON_USER_FILE_PATH)
        return json_file[discord_id]["language"]
        
    def register_user(discord_id: int, username: str, pin:str, language:str,email: Optional[str] = None):
        """
        Registers a user in the `user_data` JSON structure.

        Args:
            discord_id (int): The Discord user ID.
            username (str): The username of the Discord user.
            email (str): The email address of the user.
            full_name (Optional[str]): The full name of the user (optional).
        """
        user_data = User.get_users()
        if str(discord_id) in user_data:
            return False,f"User with ID {discord_id} is already registered."
        
        current_time = User._now_str()
        # Add user details to the dictionary
        user_data[str(discord_id)] = {
            "discord_username": username,
            "email": email,
            "pin_hash": User.hash_pin(pin),
            "balance": 0,
            "date_created": current_time,
            "date_updated": current_time,
            "language":language,
            "pin_remember_opt_in": False,
            "pin_remember_minutes": 60,
            "pin_session_created_at": "",
            "pin_session_expires_at": "",
        }
        with open(JSON_USER_FILE_PATH, 'w') as file:
                json.dump(user_data, file, indent=4)
                
        return True,f"User {username} registered successfully!"

    def update_user(discord_id: int, updates: dict):
        user_data = User.get_users()
        user_id = str(discord_id)
        if user_id not in user_data:
            return False, "User not found."
        user_data[user_id].update(updates)
        user_data[user_id]["date_updated"] = User._now_str()
        with open(JSON_USER_FILE_PATH, 'w') as file:
            json.dump(user_data, file, indent=4)
        return True, "User updated."

    def get_pin_remember_config(discord_id: int):
        user_data = User.get_users(str(discord_id))
        enabled = bool(user_data.get("pin_remember_opt_in", False))
        minutes = User._parse_minutes(user_data.get("pin_remember_minutes", 60), 60)
        expires_at = User._parse_datetime(user_data.get("pin_session_expires_at", ""))
        return {
            "enabled": enabled,
            "minutes": minutes,
            "expires_at": expires_at,
        }

    def is_pin_session_active(discord_id: int):
        config = User.get_pin_remember_config(discord_id)
        expires_at = config.get("expires_at")
        if not config.get("enabled") or not expires_at:
            return False, None
        if datetime.now() < expires_at:
            return True, expires_at
        return False, expires_at

    def set_pin_remember_settings(discord_id: int, enabled: bool, minutes: Optional[int] = None):
        updates = {"pin_remember_opt_in": enabled}
        if minutes is not None:
            updates["pin_remember_minutes"] = User._parse_minutes(minutes, 60)
        if not enabled:
            updates["pin_session_created_at"] = ""
            updates["pin_session_expires_at"] = ""
        return User.update_user(discord_id, updates)

    def start_pin_session(discord_id: int, minutes: int):
        minutes = User._parse_minutes(minutes, 60)
        now = datetime.now()
        expires_at = now + timedelta(minutes=minutes)
        updates = {
            "pin_session_created_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "pin_session_expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        return User.update_user(discord_id, updates)

    def clear_pin_session(discord_id: int):
        return User.update_user(discord_id, {
            "pin_session_created_at": "",
            "pin_session_expires_at": "",
        })
