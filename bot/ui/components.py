from __future__ import annotations

import asyncio
from typing import Callable, Dict, Iterable, List, Optional

from nextcord import ButtonStyle, Interaction, SelectOption, TextInputStyle, ui
from nextcord.ui import Button, Modal, Select, TextInput, View


class Paginator(View):
    def __init__(self, pages: List, *, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current = 0
        self.message = None

        prev_btn = Button(label="<", style=ButtonStyle.blurple)
        next_btn = Button(label=">", style=ButtonStyle.blurple)
        prev_btn.callback = self.prev_page
        next_btn.callback = self.next_page
        self.add_item(prev_btn)
        self.add_item(next_btn)

    async def prev_page(self, interaction: Interaction):
        self.current = (self.current - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    async def next_page(self, interaction: Interaction):
        self.current = (self.current + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)


class DynamicModal(Modal):
    def __init__(self, title: str, fields: Dict[str, Dict], callback_function: Callable):
        super().__init__(title=title)
        self.callback_function = callback_function
        self.inputs: Dict[str, TextInput] = {}
        for field_name, field_options in fields.items():
            text_input = TextInput(
                label=field_name,
                placeholder=field_options.get("placeholder", ""),
                required=field_options.get("required", True),
                style=field_options.get("style", TextInputStyle.short),
            )
            self.inputs[field_name] = text_input
            self.add_item(text_input)

    async def callback(self, interaction: Interaction):
        values = {field_name: input_field.value for field_name, input_field in self.inputs.items()}
        await self.callback_function(interaction, values)


class DropdownView(View):
    def __init__(self, callback: Callable, options: List[Dict], max_values: int = 1, *, placeholder: str = "Select"):
        super().__init__()
        self.callback = callback
        select = Select(
            placeholder=placeholder,
            options=[
                SelectOption(
                    label=option["label"],
                    description=option.get("description", ""),
                    value=option["value"],
                    emoji=option.get("emoji"),
                )
                for option in options
            ],
            min_values=1,
            max_values=max_values,
        )
        select.callback = self._on_select
        self.add_item(select)

    async def _on_select(self, interaction: Interaction):
        await self.callback(interaction, self.children[0].values)


class DropdownViewWithModal(View):
    def __init__(
        self,
        modal_callback: Callable,
        modal_title: str,
        modal_fields: Dict[str, Dict],
        options: List[Dict],
        max_values: int = 1,
        *,
        placeholder: str = "Select",
    ):
        super().__init__()
        self.modal_callback = modal_callback
        self.modal_title = modal_title
        self.modal_fields = modal_fields
        select = Select(
            placeholder=placeholder,
            options=[
                SelectOption(
                    label=option["label"],
                    description=option.get("description", ""),
                    value=option["value"],
                    emoji=option.get("emoji"),
                )
                for option in options
            ],
            min_values=1,
            max_values=max_values,
        )
        select.callback = self._on_select
        self.add_item(select)

    async def _on_select(self, interaction: Interaction):
        selected_option = self.children[0].values[0]
        modal = DynamicModal(
            title=self.modal_title,
            fields=self.modal_fields,
            callback_function=lambda inter, inputs: self.modal_callback(inter, {**inputs, "selected_option": selected_option}),
        )
        await interaction.response.send_modal(modal)


class ConfirmView(View):
    def __init__(self, callback: Callable, *, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.callback = callback
        yes_btn = Button(label="Yes", style=ButtonStyle.success)
        no_btn = Button(label="No", style=ButtonStyle.danger)
        yes_btn.callback = self._wrap_callback("yes")
        no_btn.callback = self._wrap_callback("no")
        self.add_item(yes_btn)
        self.add_item(no_btn)

    def _wrap_callback(self, value: str):
        async def _handler(interaction: Interaction):
            await self.callback(interaction, value)

        return _handler
