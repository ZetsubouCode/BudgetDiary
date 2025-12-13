import json

import nextcord
from nextcord.ext import commands

from _env import ENV
from bot.cogs.categories import CategoryCog
from bot.cogs.help import HelpCog
from bot.cogs.reports import ReportCog
from bot.cogs.transactions import TransactionCog
from bot.cogs.users import UserCog
from bot.config import LIST_GUILD_FILE
from bot.services import create_services
from util.logger import LoggerSingleton

logger = LoggerSingleton.get_instance(master_level=45)


def load_guild_ids():
    if LIST_GUILD_FILE.exists():
        try:
            data = json.loads(LIST_GUILD_FILE.read_text())
            if isinstance(data, dict):
                return [int(k) for k in data.keys()]
            if isinstance(data, list):
                return [int(v) for v in data]
        except Exception as exc:
            logger.log(20, f"Failed to read guild list: {exc}")
    return []


intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)
bot.remove_command("help")

services = create_services()
bot.budget_services = services


@bot.event
async def on_ready():
    logger.log(30, f"Logged in as {bot.user}")
    try:
        await bot.sync_all_application_commands()
    except Exception as exc:
        logger.log(20, f"Command sync skipped: {exc}")


@bot.event
async def on_guild_join(guild):
    logger.log(35, f"Joined guild {guild.name} ({guild.id})")
    guilds = load_guild_ids()
    if guild.id not in guilds:
        guilds.append(guild.id)
        LIST_GUILD_FILE.write_text(json.dumps(guilds, indent=2))
    try:
        await bot.sync_application_commands(guild_id=guild.id)
    except Exception as exc:
        logger.log(20, f"Could not sync commands for {guild.name}: {exc}")


def setup_cogs():
    bot.add_cog(HelpCog(bot))
    bot.add_cog(UserCog(bot, services["users"], services["categories"]))
    bot.add_cog(CategoryCog(bot, services["categories"], services["users"]))
    bot.add_cog(TransactionCog(bot, services["users"], services["categories"], services["transactions"]))
    bot.add_cog(ReportCog(bot, services["users"], services["reports"], services["exports"]))


def main():
    setup_cogs()
    try:
        bot.run(ENV.TOKEN)
    except nextcord.errors.HTTPException as exc:
        logger.log(10, f"HTTP error: {exc}")
    except Exception as exc:
        logger.log(10, f"Bot stopped: {exc}")


if __name__ == "__main__":
    main()
