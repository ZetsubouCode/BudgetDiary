from __future__ import annotations

from datetime import date

from nextcord import File, Interaction, SlashOption
from nextcord.ext import commands

from bot.config import DEFAULT_LANGUAGE, DEFAULT_REGION
from bot.services.export_service import ExportService
from bot.services.report_service import ReportService
from bot.services.user_service import UserService
from bot.ui.components import Paginator
from bot.utils.currency import format_amount, normalize_region
from bot.utils.dates import parse_date, parse_month, start_end_of_month, start_end_of_year
from bot.utils.embeds import error, success


class ReportCog(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        users: UserService,
        reports: ReportService,
        exports: ExportService,
    ):
        self.bot = bot
        self.users = users
        self.reports = reports
        self.exports = exports

    async def _profile(self, discord_id: int | str):
        user = await self.users.get_user(discord_id)
        if not user:
            return None, None, None
        language = user.get("language", DEFAULT_LANGUAGE)
        region = normalize_region(user.get("region", DEFAULT_REGION))
        return user, language, region

    def _items_to_embeds(self, title: str, report: dict, region: str) -> list:
        embeds = []
        lines = []
        for item in report["items"]:
            amount = format_amount(item.get("amount", 0), region)
            desc = item.get("description") or "-"
            extra = item.get("income_source")
            base = f"{item.get('date')} • {amount} • {item.get('category_name')}"
            if extra:
                base += f" (from {extra})"
            base += f"\n{desc}"
            lines.append(base)
            if len(lines) == 8:
                embeds.append(success(title, "\n\n".join(lines)))
                lines = []
        if lines:
            embeds.append(success(title, "\n\n".join(lines)))
        if not embeds:
            embeds.append(error(title, "No records."))
        return embeds

    @commands.slash_command(description="Show income for a specific day")
    async def daily_income(
        self,
        interaction: Interaction,
        date_value: str = SlashOption(description="DD-MM-YYYY or DDMMYYYY", required=True),
    ):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(
                embed=error("Not registered", "Register first with /register."), ephemeral=True
            )
            return
        target = parse_date(date_value)
        report = await self.reports.income_report(interaction.user.id, target, target, language, region)
        embeds = self._items_to_embeds(f"Income {target:%d-%m-%Y} • Total {report['total']}", report, region)
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            view = Paginator(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    @commands.slash_command(description="Show outcome for a specific day")
    async def daily_outcome(
        self,
        interaction: Interaction,
        date_value: str = SlashOption(description="DD-MM-YYYY or DDMMYYYY", required=True),
    ):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(
                embed=error("Not registered", "Register first with /register."), ephemeral=True
            )
            return
        target = parse_date(date_value)
        report = await self.reports.outcome_report(interaction.user.id, target, target, language, region)
        embeds = self._items_to_embeds(f"Outcome {target:%d-%m-%Y} • Total {report['total']}", report, region)
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            view = Paginator(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    @commands.slash_command(description="Show monthly income")
    async def monthly_income(
        self,
        interaction: Interaction,
        month: str = SlashOption(description="MM-YYYY or MMYYYY (blank = current)", required=False, default=None),
    ):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(embed=error("Not registered", "Register first with /register."), ephemeral=True)
            return
        month_start = parse_month(month)
        start, end = start_end_of_month(month_start)
        report = await self.reports.income_report(interaction.user.id, start, end, language, region)
        embeds = self._items_to_embeds(f"Income {month_start:%B %Y} • Total {report['total']}", report, region)
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            view = Paginator(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    @commands.slash_command(description="Show monthly outcome")
    async def monthly_outcome(
        self,
        interaction: Interaction,
        month: str = SlashOption(description="MM-YYYY or MMYYYY (blank = current)", required=False, default=None),
    ):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(embed=error("Not registered", "Register first with /register."), ephemeral=True)
            return
        month_start = parse_month(month)
        start, end = start_end_of_month(month_start)
        report = await self.reports.outcome_report(interaction.user.id, start, end, language, region)
        embeds = self._items_to_embeds(f"Outcome {month_start:%B %Y} • Total {report['total']}", report, region)
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            view = Paginator(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    @commands.slash_command(description="Show yearly outcome")
    async def yearly_outcome(
        self,
        interaction: Interaction,
        year: int = SlashOption(description="Year (YYYY)", required=True),
    ):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(embed=error("Not registered", "Register first with /register."), ephemeral=True)
            return
        start, end = start_end_of_year(year)
        report = await self.reports.outcome_report(interaction.user.id, start, end, language, region)
        embeds = self._items_to_embeds(f"Outcome {year} • Total {report['total']}", report, region)
        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            view = Paginator(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    @commands.slash_command(description="See remaining money per income type")
    async def balance(self, interaction: Interaction):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(embed=error("Not registered", "Register first with /register."), ephemeral=True)
            return
        balances = await self.reports.balances(interaction.user.id, language, region)
        lines = [
            f"{row.get('emoticon','')} **{row['name']}**\n"
            f"In: {row['in']} | Out: {row['out']} | Net: {row['balance']}"
            for row in balances
        ]
        await interaction.response.send_message(
            embed=success("Balances", "\n\n".join(lines) if lines else "No data yet."), ephemeral=True
        )

    @commands.slash_command(description="Find the largest outcome in a period")
    async def top_outcome(
        self,
        interaction: Interaction,
        period: str = SlashOption(
            description="Period type", choices={"Day": "day", "Month": "month", "Year": "year"}, required=True
        ),
        value: str = SlashOption(description="Date (DD-MM-YYYY for day, MM-YYYY for month, YYYY for year)", required=True),
    ):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(embed=error("Not registered", "Register first with /register."), ephemeral=True)
            return

        if period == "day":
            target = parse_date(value)
            start = end = target
            label = f"{target:%d-%m-%Y}"
        elif period == "month":
            start = parse_month(value)
            start, end = start_end_of_month(start)
            label = f"{start:%B %Y}"
        else:
            year = int(value)
            start, end = start_end_of_year(year)
            label = str(year)

        report = await self.reports.top_outcome(interaction.user.id, start, end, language, region)
        if not report:
            await interaction.response.send_message(embed=error("Top Outcome", "No data."), ephemeral=True)
            return

        lines = []
        largest = report.get("largest")
        if largest:
            lines.append(f"Largest: {largest['category_name']} • {largest['amount']} on {largest['date']}")
            if largest.get("description"):
                lines.append(largest["description"])
        top_cat = report.get("top_category")
        if top_cat:
            lines.append(f"Top category: {top_cat['category_name']} • {top_cat['amount']}")

        await interaction.response.send_message(
            embed=success(f"Top Outcome • {label}", "\n".join(lines)), ephemeral=True
        )

    @commands.slash_command(description="Monthly curation: incomes, outcomes, and balances")
    async def monthly_curation(
        self,
        interaction: Interaction,
        month: str = SlashOption(description="MM-YYYY or MMYYYY (blank = current)", required=False, default=None),
    ):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(embed=error("Not registered", "Register first with /register."), ephemeral=True)
            return
        month_start = parse_month(month)
        data = await self.reports.monthly_curation(interaction.user.id, month_start, language, region)

        income_lines = [f"{name}: {amount}" for name, amount in data["incomes"].items()]
        outcome_lines = [f"{name}: {amount}" for name, amount in data["outcomes"].items()]
        balance_lines = [f"{b['name']}: {b['balance']}" for b in data["balances"]]

        await interaction.response.send_message(
            embed=success(
                f"Curation {month_start:%B %Y}",
                f"Income:\n" + ("\n".join(income_lines) or "-")
                + "\n\nOutcome:\n" + ("\n".join(outcome_lines) or "-")
                + "\n\nBalances:\n" + ("\n".join(balance_lines) or "-"),
            ),
            ephemeral=True,
        )

    @commands.slash_command(description="Export monthly Excel")
    async def export_month(
        self,
        interaction: Interaction,
        month: str = SlashOption(description="MM-YYYY or MMYYYY (blank = current)", required=False, default=None),
    ):
        user, language, region = await self._profile(interaction.user.id)
        if not user:
            await interaction.response.send_message(embed=error("Not registered", "Register first with /register."), ephemeral=True)
            return
        month_start = parse_month(month)
        file_path = await self.exports.export_monthly(interaction.user.id, month_start, language, region)
        await interaction.response.send_message(
            content=f"Here is your report for {month_start:%B %Y}",
            file=File(str(file_path)),
            ephemeral=True,
        )
