import nextcord
from nextcord.ext import commands

from budget_diary.config import settings
from budget_diary.services.user_service import UserService


class Users(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.user_service = UserService()

    @nextcord.slash_command(description="Register yourself with the diary")
    async def register(
        self,
        interaction: nextcord.Interaction,
        pin: str = nextcord.SlashOption(description="Personal PIN used for confirmations"),
        language: str = nextcord.SlashOption(description="Preferred language", default=settings.default_language),
        email: str | None = nextcord.SlashOption(description="Email (optional)", required=False),
    ) -> None:  # type: ignore[override]
        success, message = self.user_service.register_user(
            interaction.user.id,
            interaction.user.name,
            pin,
            language=language,
            email=email,
        )
        await interaction.response.send_message(message, ephemeral=True)

    @nextcord.slash_command(description="Show profile and running balance")
    async def profile(self, interaction: nextcord.Interaction) -> None:  # type: ignore[override]
        summary = self.user_service.summary(interaction.user.id)
        if not summary:
            await interaction.response.send_message("Please register first with /register", ephemeral=True)
            return

        embed = nextcord.Embed(title=summary["username"], color=nextcord.Color.green())
        embed.add_field(name="Language", value=summary["language"], inline=True)
        embed.add_field(name="Email", value=summary["email"], inline=True)
        embed.add_field(name="Balance", value=summary["balance"], inline=False)
        embed.set_footer(text=f"Since {summary['created_at']}")
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Users(bot))
