import asyncio
import logging

import nextcord
from nextcord.ext import commands

from budget_diary import cogs
from budget_diary.config import settings

logging.basicConfig(level=logging.INFO)


class BudgetDiaryBot(commands.Bot):
    def __init__(self) -> None:
        intents = nextcord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        for extension in [
            "budget_diary.cogs.help",
            "budget_diary.cogs.users",
            "budget_diary.cogs.categories",
            "budget_diary.cogs.transactions",
        ]:
            await self.load_extension(extension)


def run() -> None:
    if not settings.token:
        raise RuntimeError("DISCORD_BOT_TOKEN environment variable is required")

    bot = BudgetDiaryBot()
    bot.run(settings.token)


if __name__ == "__main__":
    run()
