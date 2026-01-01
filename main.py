import os, sys, json, asyncio
import emoji
from datetime import date, datetime
from typing import Any, List, Optional, Dict, Callable

# import nextcord
from nextcord.ext import commands
from nextcord.errors import HTTPException
from nextcord import File, ButtonStyle, Embed, Color, SlashOption, Interaction, Intents,SelectOption, ui, TextInputStyle
from nextcord.ui import Button, View, Modal, TextInput, Select

from command.Command import Command as CommandFunction
from command.Category import Category as CategoryCommand
from command.Income import Income as IncomeCommand
from command.Outcome import Outcome as OutcomeCommand
from command.User import User as UserCommand

from decorator.pin import pin_required

from _env import ENV

# from util.event_handler import EventHandler
from util.text_handler import TextHandler
from util.logger import LoggerSingleton

logger = LoggerSingleton.get_instance(master_level=45)

try:
    list_guild_ids = []
    with open("list_guild.json", "r") as f:
        list_guild = json.load(f)
        for key in list_guild.keys():
            list_guild_ids.append(int(key))
            
    helpGuide = json.load(open("help.json"))
except FileNotFoundError:
    ...

Intent = Intents.all()
client = commands.Bot(command_prefix='!',intents=Intent)
client.remove_command("help")

def createHelpEmbed(data: dict, pageNum=0, limit=2, inline=False, list_page=None):
    """
    Create a paginated embed for the provided category data dynamically.
    Args:
        data (dict): The category data (Income, Outcome, etc.)
        pageNum (int): The page number to display
        limit (int): Number of items per page
        inline (bool): Whether to display fields inline
        list_page (list): List of integers indicating how many pages per category type (e.g., [2, 2])
    """
    # If list_page is not provided, default to equal distribution
    if list_page is None:
        list_page = [len(data)]  # Default: one page per category type
    
    all_categories = []
    
    # Prepare categories for pagination
    for category_name, category_items in data.items():
        category_list = []
        for key, value in category_items.items():
            category_list.append(f"{value}")
        all_categories.append((category_name, category_list))

    # Determine how many pages we have already shown from previous categories
    current_page_start = 0
    for idx, (category_name, category_items) in enumerate(all_categories):
        # Check if the current category type falls within the page range from list_page
        category_page_count = list_page[idx]
        
        if pageNum < current_page_start + category_page_count:
            # The page belongs to the current category type
            start_index = (pageNum - current_page_start) * limit
            end_index = start_index + limit
            page_data = category_items[start_index:end_index]
            
            if page_data:
                embed = Embed(color=0x0080ff, title=category_name)
                embed.add_field(name="", value="\n".join(page_data), inline=inline)
                return embed
        
        # Update current_page_start to the next category's page range
        current_page_start += category_page_count

    return None  # If no data found for this page

async def EmbedNav(ctx, data, limit=7, is_followup=False, channel=None):
    currentPage = 0
    total_pages = 0  # Will be updated when we calculate pages
    list_page = []  # List to hold how many pages each category should take

    # Get total pages based on both Income and Outcome categories
    all_categories = []
    for category, items in data.items():
        all_categories.append((category, list(items.items())))

    # Calculate the total number of pages for each category and store it in list_page
    for category_name, category_items in all_categories:
        category_page_count = (len(category_items) // limit) + (1 if len(category_items) % limit else 0)
        list_page.append(category_page_count)  # Store how many pages each category will take
        total_pages += category_page_count  # Total pages for all categories

    # Button callbacks
    async def next_callback(interaction: Interaction):
        nonlocal currentPage, sent_msg
        currentPage += 1
        if currentPage >= total_pages:
            currentPage = 0  # Reset to the first page if we go beyond the total pages

        # Create the embed and send it
        embed = createHelpEmbed(data, currentPage, limit=limit, list_page=list_page)
        if embed:
            await sent_msg.edit(embed=embed, view=myview)
        await interaction.response.defer()

    async def previous_callback(interaction: Interaction):
        nonlocal currentPage, sent_msg
        currentPage -= 1
        if currentPage < 0:
            currentPage = total_pages - 1  # Go back to the last page

        # Create the embed and send it
        embed = createHelpEmbed(data, currentPage, limit=limit, list_page=list_page)
        if embed:
            await sent_msg.edit(embed=embed, view=myview)
        await interaction.response.defer()

    # Create the previous and next buttons
    previousButton = Button(label="<", style=ButtonStyle.blurple)
    nextButton = Button(label=">", style=ButtonStyle.blurple)
    previousButton.callback = previous_callback
    nextButton.callback = next_callback

    myview = View(timeout=180)
    myview.add_item(previousButton)
    myview.add_item(nextButton)

    # Send the first message with the embed content
    embed = createHelpEmbed(data, currentPage, limit=limit, list_page=list_page)
    if embed:
        if channel:
            sent_msg = await channel.send(embed=embed, view=myview)
        else:
            if hasattr(ctx, "send"):
                sent_msg = await ctx.send(embed=embed, view=myview)
            elif is_followup:
                sent_msg = await ctx.followup.send(embed=embed, view=myview)
            else:
                sent_msg = await ctx.response.send_message(embed=embed, view=myview)

def format_currency(amount):
    try:
        amount_value = int(round(amount))
    except (TypeError, ValueError):
        amount_value = 0
    return f"Rp {amount_value:,}".replace(",", ".")

def format_category_label(name: str, emoticon: str) -> str:
    if emoticon:
        return f"{name} {emoticon}"
    return name

def build_outcome_insight_embed(data: dict) -> Embed:
    period_labels = {
        "daily": "Harian",
        "monthly": "Bulanan",
        "yearly": "Tahunan",
    }
    period_label = period_labels.get(data.get("period"), "Periode")
    embed = Embed(
        title=f"Outcome Insight - {period_label}",
        description=f"Periode: {data.get('date_label', '-')}",
        color=0xE67E22,
    )
    embed.add_field(
        name="Total Pengeluaran",
        value=f"{format_currency(data.get('total_amount', 0))}\n{data.get('transaction_count', 0)} transaksi",
        inline=False,
    )

    top_category = data.get("top_category")
    if top_category:
        category_label = format_category_label(
            top_category.get("category_name", "Kategori"),
            top_category.get("emoticon", ""),
        )
        percentage = f"{top_category.get('percentage', 0) * 100:.1f}%"
        embed.add_field(
            name="Kategori Terboros",
            value=f"{category_label}\n{format_currency(top_category.get('amount', 0))} ({percentage})",
            inline=False,
        )
    else:
        embed.add_field(name="Kategori Terboros", value="Tidak ada data.", inline=False)

    top_transaction = data.get("top_transaction")
    if top_transaction:
        transaction_label = format_category_label(
            top_transaction.get("category_name", "Kategori"),
            top_transaction.get("emoticon", ""),
        )
        detail = top_transaction.get("description") or "-"
        embed.add_field(
            name="Transaksi Termahal",
            value=(
                f"{format_currency(top_transaction.get('amount', 0))}\n"
                f"{transaction_label} | {top_transaction.get('date', '-')}\n"
                f"Detail: {detail}"
            ),
            inline=False,
        )
    else:
        embed.add_field(name="Transaksi Termahal", value="Tidak ada data.", inline=False)

    top_categories = data.get("top_categories", [])
    if top_categories:
        lines = []
        for index, item in enumerate(top_categories, start=1):
            label = format_category_label(item.get("category_name", "Kategori"), item.get("emoticon", ""))
            percentage = f"{item.get('percentage', 0) * 100:.1f}%"
            lines.append(f"{index}. {label} - {format_currency(item.get('amount', 0))} ({percentage})")
        embed.add_field(
            name=f"Top {len(top_categories)} Kategori",
            value="\n".join(lines),
            inline=False,
        )

    embed.set_footer(text="Data diambil dari transaksi outcome pada periode tersebut.")
    return embed

################################################################################################
class DynamicSelectView(ui.View):
    def __init__(self, options: Dict[str, str], callback=None):
        """
        A dynamic select menu view.

        Args:
            options (dict): A dictionary of options where key is the label and value is the value.
            callback (callable): Optional callback function to process the selected value.
        """
        super().__init__()
        self.selected_value = None  # Store the selected value
        self.event = asyncio.Event()  # Event to wait for selection
        self.callback = callback  # Store the callback function

        select_menu = ui.Select(
            placeholder="Choose an option...",
            options=[
                SelectOption(label=label, value=value)
                for label, value in options.items()
            ]
        )

        select_menu.callback = self.select_callback
        self.add_item(select_menu)

    async def select_callback(self, interaction: Interaction):
        self.selected_value = interaction.data['values'][0]  # Capture the selected value
        if self.callback:  # If a custom callback is provided, use it
            await self.callback(interaction, self.selected_value)
        else:
            await interaction.response.edit_message(
                content=f"You selected income type: **{self.selected_value}**. Processing...",
                view=None
            )
        self.event.set()  # Notify that a selection has been made

class DynamicModal(Modal):
    def __init__(self, title: str, fields: dict, callback_function):
        """
        Initialize the modal with dynamic fields based on the input dictionary.

        Args:
            title (str): The title of the modal.
            fields (dict): A dictionary where the keys are field names, and the values are dictionaries
                           with 'placeholder', 'required', and 'style' options.
            callback_function (callable): The function to call after submission.
        """
        super().__init__(title=title)
        self.callback_function = callback_function
        self.fields = fields
        self.inputs = {}  # Dictionary to hold TextInput objects

        # Dynamically create input fields
        for field_name, field_options in fields.items():
            default_value = field_options.get("default_value")
            if default_value is None:
                default_value = field_options.get("value")
            text_input = TextInput(
                label=field_name,
                placeholder=field_options.get("placeholder", ""),
                required=field_options.get("required", True),
                style=field_options.get("style", TextInputStyle.short),
                default_value=default_value,
            )
            self.inputs[field_name] = text_input
            self.add_item(text_input)

    async def callback(self, interaction: Interaction):
        """
        Callback function triggered when the modal is submitted.
        """
        # Collect user input
        user_input = {field_name: input_field.value for field_name, input_field in self.inputs.items()}
        print(f"User Input: {user_input}")

        # Call the provided callback function with the collected data
        await self.callback_function(interaction, user_input)

    def get_input_values(self) -> dict:
        """
        Get the collected user inputs as a dictionary.

        Returns:
            dict: User input values with field names as keys.
        """
        return {field_name: input_field.value for field_name, input_field in self.inputs.items()}
       
class DropdownView(View):
    def __init__(self, callback, options: list[dict], max_values=1):
        """
        :param callback: Function to call when an option is selected.
        :param options: List of dictionaries containing option details.
        """
        super().__init__()
        self.callback = callback  # Store callback function for later use

        self.dropdown = Select(
            placeholder="Choose an option...",
            options=[
                SelectOption(
                    label=option["label"],
                    description=option.get("description", ""),
                    value=option["value"],
                    emoji=option.get("emoji", None)  # Optional emoji
                ) for option in options
            ],
            min_values=1,
            max_values=max_values,
        )

        # Assign the callback function dynamically
        self.dropdown.callback = self.dropdown_callback

        # Add the dropdown to the view
        self.add_item(self.dropdown)

    async def dropdown_callback(self, interaction: Interaction):
        """Handles dropdown selection and calls the provided callback function."""
        selected_values = self.dropdown.values  # Get selected values
        await self.callback(interaction, selected_values)  # Call the provided function dynamically

class DropdownViewWithModal(View):
    def __init__(self, modal_callback,modal_title:str,modal_fields: list[dict],options: list[dict],max_values=1, title = "Choose an option..."):
        super().__init__()
        self.modal_callback = modal_callback
        self.modal_title = modal_title
        self.modal_fields = modal_fields
        # Create the dropdown
        self.dropdown = Select(
            placeholder=title,
            options=[
                SelectOption(
                    label=option["label"],
                    description=option.get("description", ""),
                    value=option["value"],
                    emoji=option.get("emoji", None)  # Optional emoji
                ) for option in options
            ],
            min_values=1,
            max_values=max_values,
        )
        self.dropdown.callback = self.dropdown_callback
        self.add_item(self.dropdown)

    def _resolve_modal_fields(self, selected_option: str):
        if callable(self.modal_fields):
            return self.modal_fields(selected_option)
        return self.modal_fields

    async def dropdown_callback(self, interaction: Interaction):
        # Get the selected value from the dropdown
        selected_option = self.dropdown.values[0]
        modal_fields = self._resolve_modal_fields(selected_option)
        # Define and send the modal
        modal = DynamicModal(
            title=self.modal_title,
            fields=modal_fields,
            callback_function=lambda interaction, inputs: self.modal_callback(interaction, {**inputs, "selected_option": selected_option}),
        )
        await interaction.response.send_modal(modal)

class DynamicEmbedWithButtons(View):
    def __init__(self, embed_title: str, embed_description: str, callback_function, list_button: list[dict], color=0x00FF00):
        """
        Initialize the embed view with dynamic buttons.

        Args:
            embed_title (str): Title of the embed.
            embed_description (str): Description of the embed.
            callback_function (callable): Function to call when a button is pressed.
            list_button (list): List of button configurations (label, style, etc.).
        """
        super().__init__(timeout=180)  # Set timeout for the buttons
        self.callback_function = callback_function
        self.message = None  # Store the message for later edits
        self.button_pressed = False  # Track if a button has been pressed

        # Create the embed
        self.embed = Embed(
            title=embed_title,
            description=embed_description,
            color=color,
        )

        # Add buttons
        for button in list_button:
            dynamic_button = Button(
                label=button.get("label"),
                style=button.get("style"),
                custom_id=button.get("custom_id")
            )
            dynamic_button.callback = self._create_button_callback(button.get("custom_id"))  # Fixed callback assignment
            self.add_item(dynamic_button)

    async def on_timeout(self):
        """Handles timeout for the buttons."""
        for child in self.children:
            child.disabled = True
        try:
            if self.message:
                await self.message.edit(view=self)  # Disable buttons in the message
        except Exception as e:
            print(f"Timeout handling error: {e}")

    def _create_button_callback(self, custom_id):
        async def callback(interaction: Interaction):
            await self._handle_button_press(interaction, custom_id)
        return callback

    async def _handle_button_press(self, interaction: Interaction, custom_id):
        """
        Handle button presses and call the callback function.

        Args:
            interaction (Interaction): The interaction object.
            custom_id (str): The custom ID of the button pressed.
        """
        # Prevent multiple presses
        if self.button_pressed:
            await interaction.response.send_message("This button has already been pressed.", ephemeral=True)
            return

        self.button_pressed = True  # Mark button as pressed

        # Disable buttons after selection
        for child in self.children:
            child.disabled = True

        try:
            # Edit the message to disable buttons first
            if self.message:
                await self.message.edit(view=self)

            # Call the provided callback function with the custom_id
            await self.callback_function(interaction, custom_id)
        except Exception as e:
            print(f"Callback function error: {e}")

    def get_embed(self) -> Embed:
        """Get the embed object."""
        return self.embed

    def set_message(self, message):
        """Set the message object for later use."""
        self.message = message

################################################################################################

@client.event
async def on_ready():
    # await client.sync_all_application_commands()
    print("we have logged in successfully as {0.user}".format(client))

@client.event
async def on_guild_join(guild):
    global list_guild_ids
    guild_id = guild.id
    guild_name = guild.name
    print(f'Bot has joined a new guild: {guild_name} (ID: {guild_id})')

    # Load existing data from the JSON file
    try:
        with open("list_guild.json", "r") as f:
            existing_guilds = json.load(f)
            if not isinstance(existing_guilds, dict):
                existing_guilds = {}
    except (FileNotFoundError, json.JSONDecodeError):
        existing_guilds = {}

    # Append the new guild ID if not already present
    list_guild_ids.clear()
    list_guild_ids.extend([int(gid) for gid in existing_guilds.keys()])
    if str(guild_id) not in existing_guilds:
        existing_guilds[str(guild_id)] = guild_name
        list_guild_ids.append(guild_id)

        # Save the updated list back to the JSON file
        with open("list_guild.json", "w") as f:
            json.dump(existing_guilds, f, indent=4)
    
    # Check if the system channel exists and if the bot can send messages there
    if guild.system_channel is not None and guild.system_channel.permissions_for(guild.me).send_messages:
        await guild.system_channel.send(f'Thanks for adding me to {guild_name}!')
        await client.sync_application_commands(guild_id=guild_id)
    else:
        print(f'Cannot send message in {guild_name}\'s system channel.')

@client.event
async def on_guild_remove(guild):
    print(f"Bot was removed from: {guild.name} (ID: {guild.id})")
    # Optional: Remove the guild from your stored data
    try:
        with open("list_guild.json", "r") as f:
            existing_guilds = json.load(f)
            if not isinstance(existing_guilds, dict):
                existing_guilds = {}
    except (FileNotFoundError, json.JSONDecodeError):
        existing_guilds = {}

    if str(guild.id) in existing_guilds:
        del existing_guilds[str(guild.id)]
        list_guild_ids.clear()
        list_guild_ids.extend([int(gid) for gid in existing_guilds.keys()])
        with open("list_guild.json", "w") as f:
            json.dump(existing_guilds, f, indent=4)
        print(f"Updated guild list after removal.")

@client.slash_command(guild_ids=list_guild_ids,name="dropdown", description="Test a dropdown menu")
async def dropdown(interaction: Interaction):
    async def handle_selection(selection_interaction: Interaction, selected_values):
        selection = ", ".join(selected_values)
        await selection_interaction.response.send_message(
            f"You selected: {selection}",
            ephemeral=True,
        )

    options = [
        {"label": "Option A", "description": "First option", "value": "A"},
        {"label": "Option B", "description": "Second option", "value": "B"},
    ]
    view = DropdownView(handle_selection, options=options, max_values=1)
    await interaction.response.send_message("Choose an option from the dropdown:", view=view, ephemeral=True)
    
@client.slash_command(guild_ids=list_guild_ids, description="send text unicode")
async def test1(interaction: Interaction):
    TextHandler.get_emoji("apple")
    TextHandler.get_emoji("cat")

    await interaction.response.send_message("ok")
    
@client.slash_command(guild_ids=list_guild_ids, description="Test Yes/No Embed")
async def yes_no_test(interaction: Interaction):
    async def handle_choice(interaction: Interaction, choice):
        """Callback function to handle the Yes/No choice."""
        if choice.lower() == "yes":
            discord_id = interaction.user.id
            discord_name = interaction.user.name
            status,message = CategoryCommand.append_template_to_json(discord_id,discord_name)
        else:
            message = f"You selected: {choice}"
            
        await interaction.channel.send(message)
        
    buttons = [
        {"label": "Yes", "style": ButtonStyle.success, "custom_id": "yes_button"},
        {"label": "No", "style": ButtonStyle.danger, "custom_id": "no_button"},
        {"label": "yanto", "style": ButtonStyle.primary, "custom_id": "test_button"}
    ]
    # Create the dynamic embed view
    embed_view = DynamicEmbedWithButtons(
        embed_title="Confirm Action",
        embed_description="Do you want to proceed?",
        callback_function=handle_choice,
        list_button=buttons
    )

    # Send the embed with the buttons
    await interaction.response.send_message(embed=embed_view.get_embed(), view=embed_view, ephemeral=True)
    # Necesary for disabling button
    sent_message = await interaction.original_message()  
    embed_view.set_message(sent_message)


@client.slash_command(guild_ids=list_guild_ids, description="Show list of command available to interact with")
async def help(interaction:Interaction):
    # await EmbedNav(interaction,helpGuide,channel=channel)
    await EmbedNav(interaction,helpGuide)

@client.slash_command(guild_ids=list_guild_ids, description="Show list of command with detail explanation")
async def menu(interaction:Interaction):
    embed = await CommandFunction.list_menu()
    await interaction.response.send_message(embed=embed)

@client.slash_command(guild_ids=list_guild_ids, description="Register yourself with the bot")
async def register(
    interaction: Interaction,
    pin: str = SlashOption(description="Your pin for your account"),
    language: str = SlashOption(description="Choose category type", choices={"Indonesia": "id", "English": "en"}, required=True, default=None),
    email: Optional[str] = SlashOption(description="Your email address", required=False, default=None),
):
    """
    Slash command for user registration.

    Args:
        interaction (Interaction): The Discord interaction object.
        email (str): The email address of the user.
        full_name (Optional[str]): The full name of the user (optional).
    """
    discord_id = interaction.user.id  # Get Discord user ID
    username = interaction.user.name  # Get Discord username
    
    async def handle_choice(interaction: Interaction, choice):
        """Callback function to handle the Yes/No choice."""
        if choice.lower() == "yes":
            discord_id = interaction.user.id
            discord_name = interaction.user.name
            status,message = CategoryCommand.append_template_to_json(discord_id,discord_name)
        else:
            message = f"You selected: {choice}"
            
        await interaction.channel.send(message)
        
    
    # Call the register_user function
    status,message = UserCommand.register_user(discord_id, username, pin, language,email)
    if status:
        buttons = [
        {"label": "Yes", "style": ButtonStyle.success, "custom_id": "yes_button"},
        {"label": "No", "style": ButtonStyle.danger, "custom_id": "no_button"}
        ]
        # Create the dynamic embed view
        embed_view = DynamicEmbedWithButtons(
            embed_title="Do you want to add template category?",
            embed_description="template category will add couples of income and outcome categories",
            callback_function=handle_choice,
            list_button=buttons
        )
        # Send the embed with the buttons
        await interaction.response.send_message(embed=embed_view.get_embed(), view=embed_view, ephemeral=True)
        sent_message = await interaction.original_message()  
        embed_view.set_message(sent_message)
    else:  
        # Send feedback to the user
        await interaction.response.send_message(message)

@client.slash_command(guild_ids=list_guild_ids, description="Manage PIN remember settings")
@pin_required(client, is_private=True)
async def pin_remember(
    interaction: Interaction,
    mode: str = SlashOption(description="Choose mode", choices={"Enable": "enable", "Disable": "disable", "Status": "status"}, required=True),
    duration_minutes: Optional[int] = SlashOption(description="Remember duration in minutes (default: current setting or 60)", required=False, default=None),
):
    discord_id = interaction.user.id
    user_data = UserCommand.get_users(str(discord_id))
    if not user_data:
        await interaction.followup.send("Please register first.", ephemeral=True)
        return

    if mode == "status":
        config = UserCommand.get_pin_remember_config(discord_id)
        expires_at = config.get("expires_at")
        if config.get("enabled"):
            if expires_at and datetime.now() < expires_at:
                remaining_minutes = int((expires_at - datetime.now()).total_seconds() // 60) + 1
                message = (
                    f"PIN remember is enabled for {config.get('minutes', 60)} minutes. "
                    f"Session active for about {remaining_minutes} minutes."
                )
            else:
                message = (
                    f"PIN remember is enabled for {config.get('minutes', 60)} minutes. "
                    "No active session. Enter PIN once to start a session."
                )
        else:
            message = "PIN remember is disabled."

        await interaction.followup.send(message, ephemeral=True)
        return

    if mode == "enable":
        if duration_minutes is None:
            config = UserCommand.get_pin_remember_config(discord_id)
            duration_minutes = config.get("minutes", 60)
        if duration_minutes <= 0:
            await interaction.followup.send("Duration must be a positive number of minutes.", ephemeral=True)
            return

        UserCommand.set_pin_remember_settings(discord_id, True, duration_minutes)
        UserCommand.start_pin_session(discord_id, duration_minutes)
        await interaction.followup.send(
            f"PIN remember enabled for {duration_minutes} minutes. Session active now.",
            ephemeral=True,
        )
        return

    if mode == "disable":
        UserCommand.set_pin_remember_settings(discord_id, False)
        await interaction.followup.send(
            "PIN remember disabled. You will be asked for PIN again.",
            ephemeral=True,
        )
        return

@client.slash_command(guild_ids=list_guild_ids, description="Show all categories (income or outcome)")
async def list_categories(interaction: Interaction, category_type: str = SlashOption(description="Choose category type", choices={"Income": "income", "Outcome": "outcome"}, required=False, default=None)):
    discord_id = str(interaction.user.id)
    
    success, message, data = await CategoryCommand.get_all(discord_id,category_type)
    if success:
        await EmbedNav(interaction,data)
    else:
        await interaction.response.send_message(message)

@client.slash_command(guild_ids=list_guild_ids, description="Menu for add new category")
@pin_required(client)
async def add_category(interaction:Interaction):
    async def handle_modal_submission(interaction:Interaction, inputs):
        discord_id = str(interaction.user.id)
        # Combine dropdown and modal inputs
        await interaction.response.defer()
        emoticon = inputs.get('Emoticon')
        if emoticon:
            emoticon = TextHandler.get_emoji(emoticon)
        status,message,data = await CategoryCommand.add(discord_id,inputs.get('Name'),inputs.get('selected_option'),emoticon)
        await interaction.followup.send(message, ephemeral=True)

    # Embed describing the interaction process
    embed = Embed(
        title="Interactive Workflow",
        description="Select a category from the dropdown and provide additional input.",
        color=0x00FF00,
    )
    fields = [
        {"label":"Income","description": "Income Category", "value": "income", "emoji": "\U0001F911"},
        {"label":"Outcome","description": "Outcome Category", "value": "outcome", "emoji": "\U0001F92B"},
    ]
    modal_fields = {
            "Name": {"placeholder": f"Enter category name", "required": True, "style": TextInputStyle.short},
            "Emoticon": {"placeholder": "Enter emoticon for the category", "required": False, "style": TextInputStyle.short},
    }
    # Attach the view
    view = DropdownViewWithModal(modal_callback=handle_modal_submission,modal_title="modal title",modal_fields=modal_fields,options=fields,max_values=1)

    # Send the initial embed with the dropdown
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@client.slash_command(guild_ids=list_guild_ids, description="Menu for edit category")
@pin_required(client)
async def edit_category(interaction:Interaction,category_type: str = SlashOption(description="Choose category type", choices={"Income": "income", "Outcome": "outcome"}, required=True)):
    
    async def handle_modal_submission(interaction:Interaction, inputs):
        discord_id = str(interaction.user.id)
        # Combine dropdown and modal inputs
        await interaction.response.defer()
        emoticon = inputs.get('Emoticon')
        emoticon_unicode = TextHandler.get_emoji(emoticon)
        if emoticon_unicode:
            emoticon = emoticon_unicode
        else:
            emoticon = ""
        
        status,message,data = await CategoryCommand.edit(discord_id,inputs.get('selected_option'),inputs.get('Name'),emoticon,category_type)

        await interaction.followup.send(message, ephemeral=True)

    discord_id = str(interaction.user.id)
    success, message, data = await CategoryCommand.get_all(discord_id,category_type,True)
    if not success:
        await interaction.followup.send(message, ephemeral=True)
        return
    if not data:
        await interaction.followup.send("No categories available.", ephemeral=True)
        return
    
    # Embed describing the interaction process
    embed = Embed(
        title="Interactive Workflow",
        description="Select a category from the dropdown and provide additional input.",
        color=0x00FF00,
    )
    fields = [
        {"label":category_type,"description":value.get("description",{}).get("en"), "value": key, "emoji":TextHandler.convert_unicode_to_emoji(value.get("emoticon",""))} for key,value in data.items()
    ]
    def build_modal_fields(selected_option: str):
        selected_data = data.get(selected_option, {})
        default_name = selected_data.get("description", {}).get("en", "")
        default_emoticon = selected_data.get("emoticon", "")
        default_emoticon = emoji.demojize(default_emoticon) if default_emoticon else ""
        return {
            "Name": {"placeholder": "Enter category name", "required": True, "style": TextInputStyle.short, "default_value": default_name},
            "Emoticon": {"placeholder": "Enter emoticon for the category", "required": False, "style": TextInputStyle.short, "default_value": default_emoticon},
        }
    # Attach the view
    view = DropdownViewWithModal(modal_callback=handle_modal_submission,modal_title="modal title",modal_fields=build_modal_fields,options=fields,max_values=1)

    # Send the initial embed with the dropdown
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
@client.slash_command(guild_ids=list_guild_ids, description="Menu for delete category")
@pin_required(client)
async def delete_category(interaction:Interaction,category_type: str = SlashOption(description="Choose category type", choices={"Income": "income", "Outcome": "outcome"}, required=True)):
    
    async def handle_submission(interaction:Interaction, selected_option):
        discord_id = str(interaction.user.id)
        # Combine dropdown and modal inputs
        selected_option = selected_option[0]
        await interaction.response.defer()
        
        status,message,data = await CategoryCommand.delete(discord_id,category_type,selected_option)

        await interaction.followup.send(message, ephemeral=True)

    discord_id = str(interaction.user.id)
    success, message, data = await CategoryCommand.get_all(discord_id,category_type,True)
    if not success:
        await interaction.followup.send(message, ephemeral=True)
        return
    if not data:
        await interaction.followup.send("No categories available.", ephemeral=True)
        return
    # Embed describing the interaction process
    embed = Embed(
        title="Interactive Workflow",
        description="Select a category from the dropdown and provide additional input.",
        color=0x00FF00,
    )
    fields = [
        {"label":category_type,"description":value.get("description",{}).get("en"), "value": key, "emoji":TextHandler.convert_unicode_to_emoji(value.get("emoticon",""))} for key,value in data.items()
    ]
    # Attach the view
    view = DropdownView(handle_submission,options=fields,max_values=1)
    # Send the initial embed with the dropdown
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@client.slash_command(guild_ids=list_guild_ids, description="Get income report for a specific date")
async def get_daily_income(interaction: Interaction,date: str = SlashOption(
        description="Enter a date (DD-MM-YYYY or DDMMYYYY)", 
        required=True
    )):
    
    discord_id = str(interaction.user.id)
    
    date = date.replace("-", "")

    try:
        # Always parse as DDMMYYYY
        date_obj = datetime.strptime(date, "%d%m%Y").date()
        formatted_date = date_obj.strftime("%d-%m-%Y")
        # Call your function
        status, message, data = await IncomeCommand.get_daily_income(discord_id, formatted_date)
        
        # Send response
        await interaction.response.send_message(message)

    except ValueError as e:
        print(e)
        await interaction.response.send_message(
            "❌ Error: Date must be in **DD-MM-YYYY** or **DDMMYYYY** format.", 
            ephemeral=True
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "❌ Something went wrong", 
            ephemeral=True
        )
        
@client.slash_command(guild_ids=list_guild_ids, description="Get monthly income report for a specific date")
async def get_monthly_income(interaction: Interaction,date: str = SlashOption(
        description="Enter a date (MM-YYYY or MMYYYY), will use current date if not filled", 
        required=False
    )):
    
    discord_id = str(interaction.user.id)
    date_input = (date or "").replace("-", "")

    try:
        # Always parse as DDMMYYYY
        if date_input:
            date_obj = datetime.strptime(date_input, "%m%Y")
        else:
            date_obj = datetime.now()
        formatted_date = date_obj.strftime("%m-%Y")
        # Call your function
        is_success, message, data = await IncomeCommand.get_monthly_income(discord_id, formatted_date)
        
        if is_success:
            await EmbedNav(interaction,data)
        else:
            await interaction.response.send_message(message)

    except ValueError as e:
        print(e)
        await interaction.response.send_message(
            "❌ Error: Date must be in **MM-YYYY** or **MMYYYY** format.", 
            ephemeral=True
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "❌ Something went wrong", 
            ephemeral=True
        )
        
@client.slash_command(guild_ids=list_guild_ids, description="Get yearly income report for a specific year")
async def get_yearly_income(interaction: Interaction,year: str = SlashOption(
        description="Enter a year YYYY), will use current date if not filled", 
        required=False
    )):
    
    discord_id = str(interaction.user.id)
    year_input = (year or "").strip()

    try:
        # Always parse as DDMMYYYY
        if year_input:
            date_obj = datetime.strptime(year_input, "%Y")
        else:
            date_obj = datetime.now()
        formatted_date = date_obj.strftime("%Y")
        # Call your function
        is_success, message, data = await IncomeCommand.get_yearly_income(discord_id, formatted_date)
        
        if is_success:
            await EmbedNav(interaction,data)
        else:
            await interaction.response.send_message(message)

    except ValueError as e:
        print(e)
        await interaction.response.send_message(
            "❌ Error: Date must be in **YYYY** or **YYYY** format.", 
            ephemeral=True
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "❌ Something went wrong", 
            ephemeral=True
        )

@client.slash_command(guild_ids=list_guild_ids, description="Insight outcome: kategori terboros dan transaksi termahal")
async def outcome_insight(
    interaction: Interaction,
    period: str = SlashOption(
        description="Pilih periode laporan",
        choices={"Harian": "daily", "Bulanan": "monthly", "Tahunan": "yearly"},
        required=True,
    ),
    date: str = SlashOption(
        description="Isi sesuai periode: DD-MM-YYYY / MM-YYYY / YYYY (kosong = sekarang)",
        required=False,
    ),
):
    discord_id = str(interaction.user.id)
    date_input = (date or "").replace("-", "")

    try:
        if period == "daily":
            date_obj = datetime.strptime(date_input, "%d%m%Y") if date_input else datetime.now()
            formatted_date = date_obj.strftime("%d-%m-%Y")
        elif period == "monthly":
            date_obj = datetime.strptime(date_input, "%m%Y") if date_input else datetime.now()
            formatted_date = date_obj.strftime("%m-%Y")
        else:
            date_obj = datetime.strptime(date_input, "%Y") if date_input else datetime.now()
            formatted_date = date_obj.strftime("%Y")

        is_success, message, data = await OutcomeCommand.get_outcome_insight(discord_id, period, formatted_date)
        if is_success:
            embed = build_outcome_insight_embed(data)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(message)

    except ValueError:
        format_hint = {
            "daily": "DD-MM-YYYY",
            "monthly": "MM-YYYY",
            "yearly": "YYYY",
        }.get(period, "DD-MM-YYYY")
        await interaction.response.send_message(
            f"ƒ?O Error: Date must be in **{format_hint}** format.",
            ephemeral=True,
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Something went wrong",
            ephemeral=True,
        )

@client.slash_command(guild_ids=list_guild_ids, description="Get outcome report for a specific date")
async def get_daily_outcome(interaction: Interaction,date: str = SlashOption(
        description="Enter a date (DD-MM-YYYY or DDMMYYYY)", 
        required=True
    )):
    
    discord_id = str(interaction.user.id)
    
    date = date.replace("-", "")

    try:
        # Always parse as DDMMYYYY
        date_obj = datetime.strptime(date, "%d%m%Y").date()
        formatted_date = date_obj.strftime("%d-%m-%Y")
        # Call your function
        status, message, data = await OutcomeCommand.get_daily_outcome(discord_id, formatted_date)
        
        # Send response
        await interaction.response.send_message(message)

    except ValueError as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Error: Date must be in **DD-MM-YYYY** or **DDMMYYYY** format.", 
            ephemeral=True
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Something went wrong", 
            ephemeral=True
        )

@client.slash_command(guild_ids=list_guild_ids, description="Get monthly outcome report for a specific date")
async def get_monthly_outcome(interaction: Interaction,date: str = SlashOption(
        description="Enter a date (MM-YYYY or MMYYYY), will use current date if not filled", 
        required=False
    )):
    
    discord_id = str(interaction.user.id)
    date_input = (date or "").replace("-", "")

    try:
        # Always parse as DDMMYYYY
        if date_input:
            date_obj = datetime.strptime(date_input, "%m%Y")
        else:
            date_obj = datetime.now()
        formatted_date = date_obj.strftime("%m-%Y")
        # Call your function
        is_success, message, data = await OutcomeCommand.get_monthly_outcome(discord_id, formatted_date)
        
        if is_success:
            await EmbedNav(interaction,data)
        else:
            await interaction.response.send_message(message)

    except ValueError as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Error: Date must be in **MM-YYYY** or **MMYYYY** format.", 
            ephemeral=True
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Something went wrong", 
            ephemeral=True
        )

@client.slash_command(guild_ids=list_guild_ids, description="Get yearly outcome report for a specific year")
async def get_yearly_outcome(interaction: Interaction,year: str = SlashOption(
        description="Enter a year YYYY), will use current date if not filled", 
        required=False
    )):
    
    discord_id = str(interaction.user.id)
    year_input = (year or "").strip()

    try:
        # Always parse as DDMMYYYY
        if year_input:
            date_obj = datetime.strptime(year_input, "%Y")
        else:
            date_obj = datetime.now()
        formatted_date = date_obj.strftime("%Y")
        # Call your function
        is_success, message, data = await OutcomeCommand.get_yearly_outcome(discord_id, formatted_date)
        
        if is_success:
            await EmbedNav(interaction,data)
        else:
            await interaction.response.send_message(message)

    except ValueError as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Error: Date must be in **YYYY** or **YYYY** format.", 
            ephemeral=True
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Something went wrong", 
            ephemeral=True
        )

@client.slash_command(guild_ids=list_guild_ids, description="Monthly summary of income and outcome grouped by category")
async def monthly_summary(interaction: Interaction,date: str = SlashOption(
        description="Enter a date (MM-YYYY or MMYYYY), will use current date if not filled", 
        required=False
    )):
    
    discord_id = str(interaction.user.id)
    date_input = (date or "").replace("-", "")

    try:
        if date_input:
            date_obj = datetime.strptime(date_input, "%m%Y")
        else:
            date_obj = datetime.now()
        formatted_date = date_obj.strftime("%m-%Y")
        is_success, message, data = await IncomeCommand.get_monthly_summary(discord_id, formatted_date)
        
        if is_success:
            await EmbedNav(interaction,data)
        else:
            await interaction.response.send_message(message)

    except ValueError as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Error: Date must be in **MM-YYYY** or **MMYYYY** format.", 
            ephemeral=True
        )
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "ƒ?O Something went wrong", 
            ephemeral=True
        )

@client.slash_command(guild_ids=list_guild_ids, description="Edit an income report for a specific date, then choose a transaction to be edited")
async def edit_income(interaction: Interaction,date: str = SlashOption(
        description="Enter a date (DD-MM-YYYY or DDMMYYYY)", 
        required=True
    )):
    
    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel
        
    discord_id = str(interaction.user.id)
    date = date.replace("-", "")

    try:
        # Always parse as DDMMYYYY
        date_obj = datetime.strptime(date, "%d%m%Y").date()
        formatted_date = date_obj.strftime("%d-%m-%Y")
        # Call your function
        status, message, data = await IncomeCommand.get_daily_income(discord_id, formatted_date)

    except ValueError as e:
        print(e)
        await interaction.response.send_message(
            "❌ Error: Date must be in **DD-MM-YYYY** or **DDMMYYYY** format.", 
            ephemeral=True
        )
        return
    except Exception as e:
        print(e)
        await interaction.response.send_message(
            "❌ Something went wrong", 
            ephemeral=True
        )
        return
    if not status:
        await interaction.response.send_message(message)
        return

    await EmbedNav(interaction,data)
    title = next(iter(data))
    list_items = list(data[title].items())
    
    message = "Please input the transaction number to choose"
    await interaction.followup.send(message)
        
    try:
        user_response = await client.wait_for("message", check=check, timeout=60)  # Wait for 60s
        transaction_number = user_response.content.strip()  # Remove extra spaces

        # Ensure the input is a valid integer
        if not transaction_number.isdigit():
            await interaction.followup.send("Invalid input! Please enter a valid transaction number. You will need to restart the command.")
            return

        transaction_number = int(transaction_number)

        # Ensure the number is within a valid range
        if transaction_number < 1 or transaction_number > len(list_items):
            await interaction.followup.send("Invalid number! Please select a valid transaction number from the list. You will need to restart the command.")
            return

        # Retrieve the selected transaction safely
        index, description = list_items[transaction_number - 1]
        await interaction.followup.send(f"You selected transaction number: {transaction_number} with index => {index}")

    except asyncio.TimeoutError:
        await interaction.followup.send("You didn't respond in time. You will need to restart the command.")

async def transfer_income_flow(interaction:Interaction):
    user_transfer_selections = {}
    discord_id = str(interaction.user.id)
    success, message, data = await CategoryCommand.get_all(discord_id, "income", True)

    if not success or not data:
        await interaction.response.send_message("No income categories available.", ephemeral=True)
        return

    if len(data) < 2:
        await interaction.response.send_message("You need at least 2 income categories to transfer.", ephemeral=True)
        return

    user_language = "en"
    try:
        user_language = UserCommand.get_user_language(discord_id)
    except Exception:
        user_language = "en"

    def resolve_category_name(category_id: str) -> str:
        category_data = data.get(category_id, {})
        return category_data.get("description", {}).get(user_language, category_id)

    # Convert data to dropdown format
    fields = [
        {"label": resolve_category_name(key), "description": resolve_category_name(key),
         "value": key, "emoji": TextHandler.convert_unicode_to_emoji(value.get("emoticon", ""))}
        for key, value in data.items()
    ]

    async def handle_modal_submission(interaction:Interaction, inputs):
        await interaction.response.defer()
        amount_input = (inputs.get("Amount") or "").strip()
        date_input = (inputs.get("Date") or "").strip()

        try:
            amount = int(amount_input)
        except ValueError:
            await interaction.followup.send("Error: Amount must be a valid number.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.followup.send("Error: Amount must be greater than 0.", ephemeral=True)
            return

        date_input = date_input.replace("-", "")

        try:
            date_obj = datetime.strptime(date_input, "%d%m%Y").date()
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            await interaction.followup.send("Error: Date must be in DD-MM-YYYY format.", ephemeral=True)
            return

        source_category = user_transfer_selections.get("source_category")
        destination_category = user_transfer_selections.get("destination_category")

        if not source_category or not destination_category:
            await interaction.followup.send("Something went wrong, please try again.", ephemeral=True)
            return

        source_name = resolve_category_name(source_category)
        destination_name = resolve_category_name(destination_category)
        status, message, data = await IncomeCommand.transfer_balance(
            discord_id,
            source_category,
            destination_category,
            amount,
            formatted_date,
            source_name,
            destination_name,
        )

        await interaction.followup.send(message, ephemeral=True)

    async def handle_first_selection(interaction: Interaction, selected_option):
        selected_source = selected_option[0]
        await interaction.response.defer()

        embed = Embed(
            title="Select Destination Category",
            description="Now, choose the category where you want to transfer the income.",
            color=0x00FF00,
        )

        view = DropdownView(
            handle_second_selection,
            options=[f for f in fields if f["value"] != selected_source],
            max_values=1
        )

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        user_transfer_selections["source_category"] = selected_source

    async def handle_second_selection(interaction: Interaction, selected_option):
        selected_destination = selected_option[0]
        user_transfer_selections["destination_category"] = selected_destination
        source_category = user_transfer_selections.get("source_category")

        if not source_category:
            await interaction.response.send_message("Something went wrong, please try again.", ephemeral=True)
            return

        default_date = datetime.now().strftime("%d-%m-%Y")
        modal_fields = {
            "Amount": {"placeholder": "Enter amount (number only)", "required": True, "style": TextInputStyle.short},
            "Date": {"placeholder": "Enter transfer date (DD-MM-YYYY)", "required": True, "style": TextInputStyle.short, "default_value": default_date},
        }
        modal = DynamicModal(
            title="Transfer balance",
            fields=modal_fields,
            callback_function=handle_modal_submission,
        )
        await interaction.response.send_modal(modal)

    embed = Embed(
        title="Select Source Category",
        description="Choose the income category you want to transfer from.",
        color=0x00FF00,
    )

    view = DropdownView(handle_first_selection, options=fields, max_values=1)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@client.slash_command(guild_ids=list_guild_ids, description="Menu for transfering income from A to B")
# @pin_required(client)
async def transfer_income(interaction:Interaction):
    await transfer_income_flow(interaction)

@client.slash_command(guild_ids=list_guild_ids, description="Transfer balance between income categories")
async def transfer(interaction:Interaction):
    await transfer_income_flow(interaction)

@client.slash_command(guild_ids=list_guild_ids, description="Add new income")
@pin_required(client)
async def add_income(interaction: Interaction):
    async def handle_modal_submission(interaction:Interaction, inputs):
        # Combine dropdown and modal inputs
        await interaction.response.defer()
        amount = inputs.get('Amount')
        detail = inputs.get('Detail')
        date = inputs.get('Date')
        # Validate Amount (integer)
        try:
            amount = int(amount)
        except ValueError:
            await interaction.followup.send("Error: Amount must be a valid number.", ephemeral=True)
            return

        date = date.replace("-", "")

        try:
            # Always parse as DDMMYYYY
            date = datetime.strptime(date, "%d%m%Y").date()
            formatted_date = date.strftime("%Y-%m-%d")
        except ValueError:
            await interaction.followup.send("Error: Date must be in DD-MM-YYYY format.", ephemeral=True)
            return
        
        status,message,data = await IncomeCommand.add(discord_id,inputs.get('selected_option'),amount,detail,formatted_date)
        await interaction.followup.send(message, ephemeral=True)

    # Embed describing the interaction process
    embed = Embed(
        title="Choose income type",
        description="Select an income type and provide additional input later.",
        color=0x00FF00,
    )
    discord_id = str(interaction.user.id)
    success, message, income_categories = await CategoryCommand.get_all(discord_id,"income",True)
    if not success:
        await interaction.followup.send(message, ephemeral=True)
        return
    if not income_categories:
        await interaction.followup.send("No income categories available.", ephemeral=True)
        return
    
    fields = [
        {"label":value.get("description",{}).get("en"),"description":value.get("description",{}).get("en"), "value": key, "emoji":TextHandler.convert_unicode_to_emoji(value.get("emoticon",""))} for key,value in income_categories.items()
    ]
    default_date = datetime.now().strftime("%d-%m-%Y")
    modal_fields = {
            "Amount": {"placeholder": "Enter amount (number only)", "required": True, "style": TextInputStyle.short},
            "Detail": {"placeholder": "Enter detail of income", "required": False, "style": TextInputStyle.short},
            "Date": {"placeholder": "Enter date income was earned (DD-MM-YYYY)", "required": True, "style": TextInputStyle.short, "default_value": default_date},
    }
    # Attach the view
    view = DropdownViewWithModal(modal_callback=handle_modal_submission,modal_title="modal title",modal_fields=modal_fields,options=fields,max_values=1)

    # Send the initial embed with the dropdown
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@client.slash_command(guild_ids=list_guild_ids, description="delete income report for a specific date")
@pin_required(client)
async def delete_income(interaction: Interaction,date: str = SlashOption(
        description="Enter a date (DD-MM-YYYY or DDMMYYYY)", 
        required=True
    )):
    discord_id = str(interaction.user.id)
    date = date.replace("-", "")
    try:
        # Always parse as DDMMYYYY
        date_obj = datetime.strptime(date, "%d%m%Y").date()
        formatted_date = date_obj.strftime("%Y-%m-%d")

    except ValueError as e:
        print(e)
        await interaction.send(
            "❌ Error: Date must be in **DD-MM-YYYY** or **DDMMYYYY** format.", 
            ephemeral=True
        )
        return
    except Exception as e:
        print(e)
        await interaction.send(
            "❌ Something went wrong", 
            ephemeral=True
        )
        return

    async def handle_submission(interaction:Interaction, selected_option):
        discord_id = str(interaction.user.id)
        # Combine dropdown and modal inputs
        selected_option = selected_option[0]
        await interaction.response.defer()
        
        status,message,data = await IncomeCommand.delete(discord_id,selected_option,formatted_date)

        await interaction.followup.send(message, ephemeral=True)
        
    success, message, data = await IncomeCommand.get_by_date(discord_id,formatted_date)
    if not success:
        await interaction.followup.send(message, ephemeral=True)
        return
    # Embed describing the interaction process
    embed = Embed(
        title="Delete income report",
        description="Select a transaction from the dropdown to be deleted.",
        color=0x00FF00,
    )
    fields = [
        {"label":f"Income {value.get('category_name',{})} ","description":f"Rp {value.get('amount',{})} - {value.get('description',{})}", "value": key, "emoji":TextHandler.convert_unicode_to_emoji(value.get('emoticon',""))} for key,value in data.items()
    ]
    # Attach the view
    view = DropdownView(handle_submission,options=fields,max_values=1)
    # Send the initial embed with the dropdown
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

@client.slash_command(guild_ids=list_guild_ids, description="Add new outcome")
@pin_required(client)
async def add_outcome(interaction: Interaction):
    discord_id = str(interaction.user.id)
    user_selections = {}
    try:
        user_language = UserCommand.get_user_language(discord_id)
    except Exception:
        user_language = "en"

    async def handle_modal_submission(interaction:Interaction, inputs):
        # Combine dropdown and modal inputs
        await interaction.response.defer()
        amount = inputs.get('Amount')
        detail = inputs.get('Detail')
        date = inputs.get('Date')
        # Validate Amount (integer)
        try:
            amount = int(amount)
        except ValueError:
            await interaction.followup.send("Error: Amount must be a valid number.", ephemeral=True)
            return

        date = date.replace("-", "")

        try:
            # Always parse as DDMMYYYY
            date = datetime.strptime(date, "%d%m%Y").date()
            formatted_date = date.strftime("%Y-%m-%d")
        except ValueError:
            await interaction.followup.send("Error: Date must be in DD-MM-YYYY format.", ephemeral=True)
            return
        
        income_category_id = user_selections.get("income_category_id")
        if not income_category_id:
            await interaction.followup.send("Something went wrong, please try again.", ephemeral=True)
            return

        status, message, data = await OutcomeCommand.add(
            discord_id,
            inputs.get('selected_option'),
            amount,
            detail,
            formatted_date,
            income_category_id,
        )
        await interaction.followup.send(message, ephemeral=True)

    success, message, income_categories = await CategoryCommand.get_all(discord_id, "income", True)
    if not success:
        await interaction.followup.send(message, ephemeral=True)
        return
    if not income_categories:
        await interaction.followup.send("No income categories available.", ephemeral=True)
        return

    balance_map = await IncomeCommand.get_income_balance_map(discord_id)
    income_label_map = {}
    income_fields = []
    for key, value in income_categories.items():
        balance = balance_map.get(str(key), 0)
        if balance <= 0:
            continue
        label = (
            value.get("description", {}).get(user_language)
            or value.get("description", {}).get("en")
            or str(key)
        )
        income_label_map[str(key)] = label
        income_fields.append({
            "label": label,
            "description": f"Available: {format_currency(balance)}",
            "value": key,
            "emoji": TextHandler.convert_unicode_to_emoji(value.get("emoticon", "")),
        })

    if not income_fields:
        await interaction.followup.send("No income categories with available balance.", ephemeral=True)
        return

    success, message, outcome_categories = await CategoryCommand.get_all(discord_id, "outcome", True)
    if not success:
        await interaction.followup.send(message, ephemeral=True)
        return
    if not outcome_categories:
        await interaction.followup.send("No outcome categories available.", ephemeral=True)
        return

    outcome_fields = [
        {
            "label": (
                value.get("description", {}).get(user_language)
                or value.get("description", {}).get("en")
                or str(key)
            ),
            "description": (
                value.get("description", {}).get(user_language)
                or value.get("description", {}).get("en")
                or str(key)
            ),
            "value": key,
            "emoji": TextHandler.convert_unicode_to_emoji(value.get("emoticon", "")),
        }
        for key, value in outcome_categories.items()
    ]

    default_date = datetime.now().strftime("%d-%m-%Y")
    modal_fields = {
            "Amount": {"placeholder": "Enter amount (number only)", "required": True, "style": TextInputStyle.short},
            "Detail": {"placeholder": "Enter detail of outcome", "required": False, "style": TextInputStyle.short},
            "Date": {"placeholder": "Enter date outcome happened (DD-MM-YYYY)", "required": True, "style": TextInputStyle.short, "default_value": default_date},
    }

    async def handle_income_selection(interaction: Interaction, selected_option):
        selected_income = selected_option[0]
        user_selections["income_category_id"] = selected_income
        income_label = income_label_map.get(str(selected_income), str(selected_income))
        await interaction.response.defer()

        embed = Embed(
            title="Choose outcome type",
            description=f"Spending from **{income_label}**. Select an outcome type and provide additional input later.",
            color=0x00FF00,
        )
        view = DropdownViewWithModal(
            modal_callback=handle_modal_submission,
            modal_title="Add outcome",
            modal_fields=modal_fields,
            options=outcome_fields,
            max_values=1,
        )
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    embed = Embed(
        title="Choose income source",
        description="Select the income category to use for this outcome.",
        color=0x00FF00,
    )
    view = DropdownView(handle_income_selection, options=income_fields, max_values=1)

    # Send the initial embed with the dropdown
    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

try:
    my_secret = ENV.TOKEN
    client.run(my_secret)
except HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system('kill 1')
    os.system("python restarter.py")
