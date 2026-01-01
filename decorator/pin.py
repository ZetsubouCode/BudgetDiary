from functools import wraps
from nextcord import Interaction, Client
from command.User import User

from util.event_handler import EventHandler

# PIN Middleware
from asyncio import TimeoutError

def pin_required(client: Client, is_private=False):
    def decorator(command_func):
        @wraps(command_func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            await interaction.response.defer(ephemeral=is_private)
            user_id = str(interaction.user.id)
            user_data = User.get_users(user_id)
            stored_pin_hash = user_data.get("pin_hash", "")
            session_active, session_expires_at = User.is_pin_session_active(user_id)
            if session_active:
                await command_func(interaction, *args, **kwargs)
                return
            if session_expires_at:
                User.clear_pin_session(user_id)

            # Send DM to the user
            try:
                # await interaction.followup.send("Check your DM to continue", ephemeral=True)
                dm_channel = await EventHandler.send_dm(interaction, "Please enter your PIN:")
                if not dm_channel:
                    await interaction.followup.send(
                        "I couldn't send you a DM. Please enable direct messages from server members.",
                        ephemeral=True,
                    )
                    return

                def check(msg):
                    return msg.author.id == interaction.user.id and msg.channel.id == dm_channel.id

                try:
                    # Wait for the user's response in DM
                    message = await client.wait_for("message", timeout=30.0, check=check)
                    entered_pin = message.content

                    # Verify PIN
                    if not User.verify_pin(entered_pin, stored_pin_hash):
                        await dm_channel.send("Incorrect PIN! Access denied.")
                        await interaction.followup.send("Incorrect PIN! Access denied.", ephemeral=is_private)
                        return

                    remember_config = User.get_pin_remember_config(user_id)
                    remember_enabled = remember_config.get("enabled", False)
                    remember_minutes = remember_config.get("minutes", 60)
                    if remember_enabled:
                        User.start_pin_session(user_id, remember_minutes)

                    channel_mention = interaction.channel.mention if interaction.channel else "the original channel"
                    guild_name = interaction.guild.name if interaction.guild else "the server"
                    await dm_channel.send(
                        (
                            f"PIN verified. Remembered for {remember_minutes} minutes. "
                            f"Please continue in {channel_mention} on {guild_name}."
                        ) if remember_enabled else
                        f"PIN verified. Please continue in {channel_mention} on {guild_name}."
                    )
                    await command_func(interaction, *args, **kwargs)

                except TimeoutError:
                    await dm_channel.send("You took too long to respond. Try again.")
                    await interaction.followup.send("You took too long to respond. Try again.", ephemeral=is_private)

            except Exception as e:
                print(f"Error in PIN verification: {e}")
                await interaction.followup.send("An error occurred. Please try again.")

        return wrapper
    return decorator
