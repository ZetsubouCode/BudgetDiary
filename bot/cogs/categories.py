from __future__ import annotations

from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from bot.config import DEFAULT_LANGUAGE
from bot.services.category_service import CategoryService
from bot.services.user_service import UserService
from bot.ui.components import Paginator
from bot.utils.embeds import error, success


class CategoryCog(commands.Cog):
    def __init__(self, bot: commands.Bot, categories: CategoryService, users: UserService):
        self.bot = bot
        self.categories = categories
        self.users = users

    async def _language(self, discord_id: int | str) -> str:
        user = await self.users.get_user(discord_id)
        return user.get("language", DEFAULT_LANGUAGE) if user else DEFAULT_LANGUAGE

    @commands.slash_command(description="List your income/outcome categories")
    async def list_categories(
        self,
        interaction: Interaction,
        category_type: str = SlashOption(
            description="Filter by category type",
            choices={"Income": "income", "Outcome": "outcome"},
            required=False,
            default=None,
        ),
    ):
        language = await self._language(interaction.user.id)
        ok, _, categories = await self.categories.list_categories(interaction.user.id, category_type)
        if not ok:
            await interaction.response.send_message(embed=error("Categories", "No categories found."), ephemeral=True)
            return

        embeds = []
        for cat_type, cat_map in categories.items():
            lines = []
            for cid, payload in cat_map.items():
                desc = payload.get("description", {})
                name = desc.get(language) or desc.get("en") or desc.get("id") or desc.get("INA") or f"#{cid}"
                emo = payload.get("emoticon", "")
                lines.append(f"`{cid}` {emo} {name}")
            content = "\n".join(lines) if lines else "No categories yet."
            embeds.append(success(cat_type.title(), content))

        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        else:
            view = Paginator(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    @commands.slash_command(description="Add a new category")
    async def add_category(
        self,
        interaction: Interaction,
        category_type: str = SlashOption(
            description="Income or Outcome", choices={"Income": "income", "Outcome": "outcome"}
        ),
        name: str = SlashOption(description="Category name"),
        emoticon: str = SlashOption(description="Emoji (optional)", required=False, default=""),
    ):
        language = await self._language(interaction.user.id)
        ok, message, new_id = await self.categories.add_category(
            interaction.user.id, category_type, name, emoticon, language
        )
        builder = success if ok else error
        await interaction.response.send_message(
            embed=builder("Add Category", f"{message} (id: {new_id})" if ok else message), ephemeral=True
        )

    @commands.slash_command(description="Edit an existing category")
    async def edit_category(
        self,
        interaction: Interaction,
        category_type: str = SlashOption(
            description="Income or Outcome", choices={"Income": "income", "Outcome": "outcome"}
        ),
        category_id: str = SlashOption(description="Category ID to edit"),
        name: str = SlashOption(description="New name", required=False, default=None),
        emoticon: str = SlashOption(description="New emoji (optional)", required=False, default=None),
    ):
        language = await self._language(interaction.user.id)
        ok, message, _ = await self.categories.edit_category(
            interaction.user.id, category_type, category_id, name, emoticon, language
        )
        builder = success if ok else error
        await interaction.response.send_message(embed=builder("Edit Category", message), ephemeral=True)

    @commands.slash_command(description="Soft delete a category")
    async def delete_category(
        self,
        interaction: Interaction,
        category_type: str = SlashOption(
            description="Income or Outcome", choices={"Income": "income", "Outcome": "outcome"}
        ),
        category_id: str = SlashOption(description="Category ID to delete"),
    ):
        ok, message = await self.categories.delete_category(interaction.user.id, category_type, category_id)
        builder = success if ok else error
        await interaction.response.send_message(embed=builder("Delete Category", message), ephemeral=True)
