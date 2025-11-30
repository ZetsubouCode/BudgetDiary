from dataclasses import dataclass
from pathlib import Path
import os


@dataclass
class Settings:
    """Application configuration pulled from environment variables."""

    token: str | None = os.getenv("DISCORD_BOT_TOKEN")
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "en")
    data_dir: Path = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parent.parent / "data"))

    @property
    def users_file(self) -> Path:
        return self.data_dir / "users.json"

    @property
    def categories_file(self) -> Path:
        return self.data_dir / "categories.json"

    @property
    def transactions_file(self) -> Path:
        return self.data_dir / "transactions.json"

    @property
    def category_template_file(self) -> Path:
        return self.data_dir / "templates" / "categories.json"


settings = Settings()
