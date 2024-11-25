import json, hashlib
from util.date_utils import Util
from util.logger import LoggerSingleton
from typing import Optional
from config.config import *

class User:
    logger = LoggerSingleton.get_instance()
    
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
     
    def get_users(category_type=""):
        file_path = JSON_USER_FILE_PATH
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        
    def register_user(discord_id: int, username: str, pin=str, email: Optional[str] = None):
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
        
        # Add user details to the dictionary
        user_data[str(discord_id)] = {
            "discord_username": username,
            "email": email,
            "pin_hash": User.hash_pin(pin),
        }
        with open(JSON_USER_FILE_PATH, 'w') as file:
                json.dump(user_data, file, indent=4)
                
        return True,f"User {username} registered successfully!"