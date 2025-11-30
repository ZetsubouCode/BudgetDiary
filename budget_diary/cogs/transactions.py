import nextcord
from nextcord.ext import commands

from budget_diary.services.transaction_service import TransactionService


class Transactions(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.transaction_service = TransactionService()

    @nextcord.slash_command(description="Record an income or outcome")
    async def transaction(
        self,
        interaction: nextcord.Interaction,
        amount: float = nextcord.SlashOption(description="Amount"),
        category_type: str = nextcord.SlashOption(
            description="income or outcome", choices={"income": "income", "outcome": "outcome"}
        ),
        category: str = nextcord.SlashOption(description="Category name"),
        note: str | None = nextcord.SlashOption(description="Optional note", required=False),
    ) -> None:  # type: ignore[override]
        success, message = self.transaction_service.add_transaction(
            interaction.user.id, amount, category_type, category, note
        )
        await interaction.response.send_message(message, ephemeral=True)

    @nextcord.slash_command(description="Show your recent transactions")
    async def recent(
        self,
        interaction: nextcord.Interaction,
        limit: int = nextcord.SlashOption(description="How many rows", default=5, min_value=1, max_value=15),
    ) -> None:  # type: ignore[override]
        rows = self.transaction_service.recent_transactions(interaction.user.id, limit)
        if not rows:
            await interaction.response.send_message("No transactions recorded yet", ephemeral=True)
            return

        embed = nextcord.Embed(title="Recent transactions")
        for txn in rows:
            sign = "+" if txn.category_type == "income" else "-"
            amount = f"{sign}${abs(txn.amount):,.2f}"
            embed.add_field(
                name=f"{txn.category} ({txn.category_type})",
                value=f"{amount}\n{txn.created_at.strftime('%Y-%m-%d %H:%M')}\n{txn.note or ''}",
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Transactions(bot))
