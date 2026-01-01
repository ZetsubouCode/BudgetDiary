import nextcord
from nextcord.ext import commands


class Help(commands.Cog):
    """Simple help menu showing the main flows."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @nextcord.slash_command(description="Show available commands")
    async def help(self, interaction: nextcord.Interaction) -> None:  # type: ignore[override]
        embed = nextcord.Embed(
            title="Budget Diary",
            description="Track income and outcome with lightweight JSON storage.",
            color=nextcord.Color.blue(),
        )
        embed.add_field(name="/register", value="Create your account with a PIN", inline=False)
        embed.add_field(name="/profile", value="Show language, email, and balance", inline=False)
        embed.add_field(name="/categories", value="List or add categories", inline=False)
        embed.add_field(name="/transaction", value="Add or list transactions", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Help(bot))
