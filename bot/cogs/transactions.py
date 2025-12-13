from __future__ import annotations

from datetime import date

from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from bot.config import DEFAULT_REGION
from decorator.pin import pin_required
from bot.services.category_service import CategoryService
from bot.services.transaction_service import TransactionService
from bot.services.user_service import UserService
from bot.ui.components import ConfirmView, DropdownView, DropdownViewWithModal, DynamicModal
from bot.utils.currency import format_amount, normalize_region
from bot.utils.dates import parse_date
from bot.utils.embeds import error, success


class TransactionCog(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        users: UserService,
        categories: CategoryService,
        transactions: TransactionService,
    ):
        self.bot = bot
        self.users = users
        self.categories = categories
        self.transactions = transactions

    async def _region(self, discord_id: int | str) -> str:
        user = await self.users.get_user(discord_id)
        return normalize_region(user.get("region") if user else DEFAULT_REGION)

    @commands.slash_command(description="Record new income")
    @pin_required()
    async def add_income(self, interaction: Interaction):
        user = await self.users.get_user(interaction.user.id)
        if not user:
            await interaction.response.send_message(
                embed=error("Not registered", "Register first with /register."), ephemeral=True
            )
            return

        _, _, income_categories = await self.categories.list_categories(interaction.user.id, "income", raw_data=True)
        if not income_categories:
            await interaction.response.send_message(
                embed=error("Income", "Add at least one income category first."), ephemeral=True
            )
            return

        fields = [
            {
                "label": value.get("description", {}).get(user.get("language", "en"), f"Category {cid}"),
                "description": f"#{cid}",
                "value": cid,
                "emoji": value.get("emoticon", ""),
            }
            for cid, value in income_categories.items()
            if not value.get("is_deleted")
        ]

        region = await self._region(interaction.user.id)
        modal_fields = {
            "Amount": {"placeholder": "Enter amount (numbers only)", "required": True},
            "Description": {"placeholder": "Optional description", "required": False},
            "Date": {"placeholder": "DD-MM-YYYY (blank = today)", "required": False},
        }

        async def handle_modal(inter: Interaction, inputs):
            try:
                amount = float(inputs.get("Amount"))
            except (TypeError, ValueError):
                await inter.response.send_message(
                    embed=error("Invalid amount", "Amount must be a number."), ephemeral=True
                )
                return
            if amount <= 0:
                await inter.response.send_message(
                    embed=error("Invalid amount", "Amount must be greater than zero."), ephemeral=True
                )
                return
            if amount <= 0:
                await inter.response.send_message(
                    embed=error("Invalid amount", "Amount must be greater than zero."), ephemeral=True
                )
                return
            if amount <= 0:
                await inter.response.send_message(
                    embed=error("Invalid amount", "Amount must be greater than zero."), ephemeral=True
                )
                return
            date_value = parse_date(inputs.get("Date")) if inputs.get("Date") else date.today()
            ok, msg, record = await self.transactions.add_income(
                interaction.user.id, inputs.get("selected_option"), amount, inputs.get("Description", ""), date_value, region
            )
            builder = success if ok else error
            await inter.response.send_message(
                embed=builder(
                    "Income saved",
                    f"{msg}\n{format_amount(amount, region)} on {record.get('date')}",
                ),
                ephemeral=True,
            )

        view = DropdownViewWithModal(
            modal_callback=handle_modal,
            modal_title="Income detail",
            modal_fields=modal_fields,
            options=fields,
            max_values=1,
            placeholder="Choose income type",
        )

        await interaction.followup.send(
            embed=success("Add Income", "Pick an income type, then fill the form."), view=view, ephemeral=True
        )

    @commands.slash_command(description="Record new outcome")
    @pin_required()
    async def add_outcome(self, interaction: Interaction):
        user = await self.users.get_user(interaction.user.id)
        if not user:
            await interaction.response.send_message(
                embed=error("Not registered", "Register first with /register."), ephemeral=True
            )
            return

        # Load categories
        _, _, income_cats = await self.categories.list_categories(interaction.user.id, "income", raw_data=True)
        _, _, outcome_cats = await self.categories.list_categories(interaction.user.id, "outcome", raw_data=True)

        if not income_cats or not outcome_cats:
            await interaction.response.send_message(
                embed=error("Outcome", "Ensure you have income and outcome categories first."), ephemeral=True
            )
            return

        language = user.get("language", "en")
        income_fields = [
            {
                "label": value.get("description", {}).get(language, f"Income {cid}"),
                "description": f"#{cid}",
                "value": cid,
                "emoji": value.get("emoticon", ""),
            }
            for cid, value in income_cats.items()
            if not value.get("is_deleted")
        ]
        outcome_fields = [
            {
                "label": value.get("description", {}).get(language, f"Outcome {cid}"),
                "description": f"#{cid}",
                "value": cid,
                "emoji": value.get("emoticon", ""),
            }
            for cid, value in outcome_cats.items()
            if not value.get("is_deleted")
        ]
        selection = {}

        async def income_selected(inter: Interaction, values):
            selection["income"] = values[0]
            await inter.response.edit_message(
                embed=success("Income chosen", "Now choose the outcome category."), view=None
            )
            view_outcome = DropdownView(outcome_selected, options=outcome_fields, placeholder="Outcome category")
            await inter.followup.send(
                embed=success("Outcome", "Pick an outcome category to continue."), view=view_outcome, ephemeral=True
            )

        async def outcome_selected(inter: Interaction, values):
            selection["outcome"] = values[0]
            modal_fields = {
                "Amount": {"placeholder": "Enter amount (numbers only)", "required": True},
                "Description": {"placeholder": "Optional description", "required": False},
                "Date": {"placeholder": "DD-MM-YYYY (blank = today)", "required": False},
            }
            modal = DynamicModal("Outcome detail", modal_fields, submit_outcome)
            await inter.response.send_modal(modal)

        async def submit_outcome(inter: Interaction, inputs):
            try:
                amount = float(inputs.get("Amount"))
            except (TypeError, ValueError):
                await inter.response.send_message(
                    embed=error("Invalid amount", "Amount must be a number."), ephemeral=True
                )
                return
            spend_date = parse_date(inputs.get("Date")) if inputs.get("Date") else date.today()
            ok, msg, record = await self.transactions.add_outcome(
                interaction.user.id,
                selection.get("outcome"),
                selection.get("income"),
                amount,
                inputs.get("Description", ""),
                spend_date,
                await self._region(interaction.user.id),
            )
            builder = success if ok else error
            await inter.response.send_message(
                embed=builder(
                    "Outcome saved",
                    f"{msg}\n{format_amount(amount, await self._region(interaction.user.id))} on {record.get('date')}",
                ),
                ephemeral=True,
            )

        income_view = DropdownView(income_selected, options=income_fields, placeholder="Pick income source")
        await interaction.followup.send(
            embed=success("Add Outcome", "Pick the income source to spend from."), view=income_view, ephemeral=True
        )

    @commands.slash_command(description="Transfer balance between your income types")
    @pin_required()
    async def transfer_income(self, interaction: Interaction):
        user = await self.users.get_user(interaction.user.id)
        if not user:
            await interaction.response.send_message(
                embed=error("Not registered", "Register first with /register."), ephemeral=True
            )
            return

        _, _, income_cats = await self.categories.list_categories(interaction.user.id, "income", raw_data=True)
        language = user.get("language", "en")
        income_fields = [
            {
                "label": value.get("description", {}).get(language, f"Income {cid}"),
                "description": f"#{cid}",
                "value": cid,
                "emoji": value.get("emoticon", ""),
            }
            for cid, value in income_cats.items()
            if not value.get("is_deleted")
        ]
        selection = {}

        async def source_selected(inter: Interaction, values):
            selection["source"] = values[0]
            await inter.response.edit_message(
                embed=success("Source selected", "Pick the destination income type."), view=None
            )
            dest_fields = [field for field in income_fields if field["value"] != selection["source"]]
            dest_view = DropdownView(destination_selected, options=dest_fields, placeholder="Destination income")
            await inter.followup.send(
                embed=success("Destination", "Select where to transfer to."), view=dest_view, ephemeral=True
            )

        async def destination_selected(inter: Interaction, values):
            selection["destination"] = values[0]
            modal_fields = {
                "Amount": {"placeholder": "Enter amount (numbers only)", "required": True},
                "Note": {"placeholder": "Optional note", "required": False},
            }
            modal = DynamicModal("Confirm transfer", modal_fields, confirm_transfer)
            await inter.response.send_modal(modal)

        async def confirm_transfer(inter: Interaction, inputs):
            try:
                amount = float(inputs.get("Amount"))
            except (TypeError, ValueError):
                await inter.response.send_message(
                    embed=error("Invalid amount", "Amount must be a number."), ephemeral=True
                )
                return
            note = inputs.get("Note", "")
            summary = (
                f"Transfer {format_amount(amount, await self._region(interaction.user.id))}\n"
                f"From: {selection.get('source')} -> To: {selection.get('destination')}\nNote: {note or '-'}"
            )

            async def on_confirm(confirm_inter: Interaction, decision: str):
                if decision == "yes":
                    ok, msg, _ = await self.transactions.transfer_income(
                        interaction.user.id, selection["source"], selection["destination"], amount, note
                    )
                    builder = success if ok else error
                    await confirm_inter.response.send_message(embed=builder("Transfer", msg), ephemeral=True)
                else:
                    await confirm_inter.response.send_message(embed=error("Transfer", "Cancelled."), ephemeral=True)

            view = ConfirmView(on_confirm)
            await inter.response.send_message(
                embed=success("Confirm transfer", summary), view=view, ephemeral=True
            )

        income_view = DropdownView(source_selected, options=income_fields, placeholder="Pick source income")
        await interaction.followup.send(
            embed=success("Transfer", "Pick the source income type."), view=income_view, ephemeral=True
        )
