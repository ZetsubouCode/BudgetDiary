from __future__ import annotations

from nextcord import Interaction
from nextcord.ext import commands

from bot.utils.embeds import success


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="What can this bot do?")
    async def help(self, interaction: Interaction):
        description = (
            "BudgetDiary tracks income/outcome per user with PIN-protected actions.\n"
            "Use slash commands to add income/outcome, transfer between income types, "
            "view daily/monthly/yearly reports, see balances, export Excel, and manage categories."
        )
        embed = success("BudgetDiary", description)
        embed.add_field(
            name="Getting started",
            value="1) /register\n2) /add_category\n3) /add_income or /add_outcome\n4) /balance",
            inline=False,
        )
        embed.add_field(
            name="Reports",
            value="/daily_income /daily_outcome /monthly_income /monthly_outcome /yearly_outcome /top_outcome /monthly_curation",
            inline=False,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
