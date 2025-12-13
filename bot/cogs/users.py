from __future__ import annotations

from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from bot.config import DEFAULT_LANGUAGE, DEFAULT_REGION, REGIONS
from bot.services.category_service import CategoryService
from bot.services.user_service import UserService
from bot.utils.currency import normalize_region
from bot.utils.embeds import error, success


class UserCog(commands.Cog):
    def __init__(self, bot: commands.Bot, users: UserService, categories: CategoryService):
        self.bot = bot
        self.users = users
        self.categories = categories

    @commands.slash_command(description="Register yourself and set your PIN")
    async def register(
        self,
        interaction: Interaction,
        pin: str = SlashOption(description="4-10 digit PIN for balance actions"),
        language: str = SlashOption(description="Language code (en/id)", required=False, default=DEFAULT_LANGUAGE),
        region: str = SlashOption(
            description="Region to format currency",
            choices={r.title(): r for r in REGIONS.keys()},
            required=False,
            default=DEFAULT_REGION,
        ),
        email: str = SlashOption(description="Optional email", required=False, default=None),
    ):
        if not (4 <= len(pin) <= 10 and pin.isdigit()):
            await interaction.response.send_message(
                embed=error("Invalid PIN", "PIN must be 4-10 digits."), ephemeral=True
            )
            return

        status, message = await self.users.register(
            interaction.user.id, interaction.user.name, pin, language.lower(), region.upper(), email
        )
        if status:
            await self.categories.ensure_user_categories(interaction.user.id)
            await interaction.response.send_message(embed=success("Registered", message), ephemeral=True)
        else:
            await interaction.response.send_message(embed=error("Register", message), ephemeral=True)

    @commands.slash_command(description="Update your currency region")
    async def set_region(
        self,
        interaction: Interaction,
        region: str = SlashOption(
            description="Region", choices={r.title(): r for r in REGIONS.keys()}, required=True
        ),
    ):
        status, message = await self.users.update_region(interaction.user.id, normalize_region(region))
        embed_builder = success if status else error
        await interaction.response.send_message(embed=embed_builder("Region", message), ephemeral=True)

    @commands.slash_command(description="Update your preferred language for categories")
    async def set_language(
        self,
        interaction: Interaction,
        language: str = SlashOption(description="Language code (en/id)", required=True),
    ):
        status, message = await self.users.update_language(interaction.user.id, language.lower())
        embed_builder = success if status else error
        await interaction.response.send_message(embed=embed_builder("Language", message), ephemeral=True)

    @commands.slash_command(description="See your profile and settings")
    async def profile(self, interaction: Interaction):
        user = await self.users.get_user(interaction.user.id)
        if not user:
            await interaction.response.send_message(
                embed=error("Not registered", "Run /register to start."), ephemeral=True
            )
            return
        await interaction.response.send_message(
            embed=success(
                "Profile",
                f"User: {interaction.user.name}\nRegion: {user.get('region', DEFAULT_REGION)}\n"
                f"Language: {user.get('language', DEFAULT_LANGUAGE)}\n"
                f"Email: {user.get('email', '-')}",
            ),
            ephemeral=True,
        )
