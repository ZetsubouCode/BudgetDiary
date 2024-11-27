from functools import wraps
from nextcord import Interaction, Client
from nextcord.errors import NotFound,Forbidden
from command.User import User

from util.event_handler import EventHandler

# PIN Middleware
from nextcord.errors import Forbidden, NotFound
from asyncio import TimeoutError

def pin_required(client: Client, is_private=False):
    def decorator(command_func):
        @wraps(command_func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            print("masuk????????????")
            await interaction.response.defer(ephemeral=is_private)
            user_id = str(interaction.user.id)
            user_data = User.get_users(user_id)
            stored_pin_hash = user_data.get("pin_hash", "")

            # Send DM to the user
            try:
                # await interaction.followup.send("Check your DM to continue", ephemeral=True)
                dm_channel = await EventHandler.send_dm(interaction, "Please enter your PIN:")
                if not dm_channel:
                    await interaction.response.send_message(
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
                        return
                    
                    await dm_channel.send(f"Your PIN is verified successfully. Please go back check the channel **{interaction.channel}** on **{interaction.guild.name}**")
                    await command_func(interaction, *args, **kwargs)

                except TimeoutError:
                    await dm_channel.send("You took too long to respond. Try again.")

            except Exception as e:
                print(f"Error in PIN verification: {e}")
                await interaction.response.send_message("An error occurred. Please try again.", ephemeral=True)

        return wrapper
    return decorator
