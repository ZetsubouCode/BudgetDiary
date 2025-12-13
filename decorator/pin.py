from functools import wraps
from typing import Any, Callable, Tuple

from asyncio import TimeoutError
from nextcord import Interaction

from bot.config import PIN_TIMEOUT_SECONDS
from util.event_handler import EventHandler


def _split_args(args: Tuple[Any]) -> Tuple[Any, Interaction, Tuple[Any, ...]]:
    """Return (maybe_self, interaction, rest_args)."""
    if isinstance(args[0], Interaction):
        return None, args[0], args[1:]
    return args[0], args[1], args[2:]


def pin_required(is_private: bool = True):
    """
    Decorator that requests PIN over DM before executing the command.
    Expects the bot instance to expose .budget_services['users'].
    """

    def decorator(command_func: Callable):
        @wraps(command_func)
        async def wrapper(*args, **kwargs):
            maybe_self, interaction, remaining = _split_args(args)
            await interaction.response.defer(ephemeral=is_private)

            bot = interaction.client
            services = getattr(bot, "budget_services", {})
            user_service = services.get("users")
            if not user_service:
                await interaction.followup.send("PIN system not available.", ephemeral=True)
                return

            user_id = str(interaction.user.id)
            user_data = await user_service.get_user(user_id)
            if not user_data or "pin_hash" not in user_data:
                await interaction.followup.send("Register and set your PIN first with /register.", ephemeral=True)
                return

            try:
                dm_channel = await EventHandler.send_dm(interaction, "Please enter your PIN to continue:")
                if not dm_channel:
                    await interaction.followup.send(
                        "I couldn't DM you. Please allow direct messages from server members.", ephemeral=True
                    )
                    return

                def check(msg):
                    return msg.author.id == interaction.user.id and msg.channel.id == dm_channel.id

                try:
                    message = await bot.wait_for("message", timeout=PIN_TIMEOUT_SECONDS, check=check)
                    entered_pin = message.content
                except TimeoutError:
                    await dm_channel.send("You took too long to respond. Try again.")
                    return

                if not await user_service.verify_pin(user_id, entered_pin):
                    await dm_channel.send("Incorrect PIN! Access denied.")
                    return

                await dm_channel.send(
                    f"PIN verified. Continue in **{interaction.channel}** on **{interaction.guild.name}**."
                )
                if maybe_self:
                    await command_func(maybe_self, interaction, *remaining, **kwargs)
                else:
                    await command_func(interaction, *remaining, **kwargs)

            except Exception as exc:
                print(f"Error in PIN verification: {exc}")
                await interaction.followup.send("An error occurred. Please try again.", ephemeral=True)

        return wrapper

    return decorator
