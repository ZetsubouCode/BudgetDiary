import nextcord
from nextcord.ext import commands

from budget_diary.services.category_service import CategoryService


class Categories(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.category_service = CategoryService()

    @nextcord.slash_command(description="List your categories")
    async def categories(
        self,
        interaction: nextcord.Interaction,
        category_type: str = nextcord.SlashOption(
            description="Type of category", choices={"income": "income", "outcome": "outcome"}, default="income"
        ),
    ) -> None:  # type: ignore[override]
        categories = self.category_service.list_categories(interaction.user.id, category_type)[category_type]
        if not categories:
            await interaction.response.send_message("No categories found", ephemeral=True)
            return

        embed = nextcord.Embed(title=f"{category_type.title()} categories")
        for cat in categories:
            emoji = f" {cat.emoji}" if cat.emoji else ""
            embed.add_field(name=cat.name, value=f"{cat.category_type}{emoji}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.slash_command(description="Add a new category")
    async def add_category(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(description="Category name"),
        category_type: str = nextcord.SlashOption(
            description="income or outcome", choices={"income": "income", "outcome": "outcome"}, default="outcome"
        ),
        emoji: str | None = nextcord.SlashOption(description="Emoji (optional)", required=False),
    ) -> None:  # type: ignore[override]
        success, message = self.category_service.add_category(interaction.user.id, name, category_type, emoji)
        await interaction.response.send_message(message, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Categories(bot))
