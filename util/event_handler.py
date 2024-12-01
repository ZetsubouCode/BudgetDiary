from nextcord import Forbidden, Interaction

class EventHandler:
    @staticmethod
    async def send_dm(interaction: Interaction, message: str):
        try:
            user = interaction.user
            print(f"Attempting to send DM to {user.name} ({user.id})")
            dm_channel = await user.create_dm()
            await dm_channel.send(message)
            print(f"Message sent to {user.name} ({user.id}) in DM channel {dm_channel.id}")
            return dm_channel
        except Forbidden:
            print(f"Could not send message to {user.name} ({user.id}). They might have DMs disabled.")
            return None
        except Exception as e:
            print(f"An error occurred while sending DM: {e}")
            return None
