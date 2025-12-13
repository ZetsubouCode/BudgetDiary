from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "store"
TEMPLATE_DIR = BASE_DIR / "data" / "template"
EXPORT_DIR = BASE_DIR / "data" / "export"
HELP_FILE = BASE_DIR / "help.json"
LIST_GUILD_FILE = BASE_DIR / "list_guild.json"

USERS_FILE = DATA_DIR / "users.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

CATEGORY_TEMPLATE_FILE = TEMPLATE_DIR / "category.json"
TRANSACTION_TEMPLATE_FILE = TEMPLATE_DIR / "transaction.json"

DEFAULT_LANGUAGE = "en"
DEFAULT_REGION = "USA"

REGIONS = {
    "USA": {"currency": "USD", "symbol": "$", "precision": 2},
    "JAPAN": {"currency": "JPY", "symbol": "¥", "precision": 0},
    "INDONESIA": {"currency": "IDR", "symbol": "Rp", "precision": 0},
}

DATE_FMT = "%Y-%m-%d"
PIN_TIMEOUT_SECONDS = 45

# ensure folders exist eagerly
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
