import os, sys, json, asyncio
import emoji
from datetime import date
from typing import Any, List, Optional, Dict, Callable

import nextcord
from nextcord.ext import commands
from nextcord.errors import HTTPException
from nextcord import File, ButtonStyle, Embed, Color, SlashOption, Interaction, Intents,SelectOption, ui, TextInputStyle
from nextcord.ui import Button, View, Modal, TextInput, Select

from command.Command import Command as CommandFunction
from command.Category import Category as CategoryCommand
from command.User import User as UserCommand

from decorator.pin import pin_required

from temp_db import temp_db
from _env import ENV

from util.event_handler import EventHandler
from util.logger import LoggerSingleton

logger = LoggerSingleton.get_instance(master_level=45)

try:
    list_guild_ids = []
    with open("list_guild.json", "r") as f:
        list_guild = json.load(f)
        for key in list_guild.keys():
            list_guild_ids.append(int(key))
except FileNotFoundError:
    ...

Intent = Intents.all()
client = commands.Bot(command_prefix='!',intents=Intent)
client.remove_command("help")

helpGuide = json.load(open("help.json"))

def JSON_convert(array:List[Any]):
        temp_json = {}
        for data in array:
            temp_json[data["description"]["INA"]] = data["id"]
        return json.loads(json.dumps(temp_json))

# category =  json.load(open("data\category.json"))
# temp_db._category = category["outcome"]
# categoryJSON = JSON_convert(category["outcome"])
# temp_db._income_type = category["income"]
# income_typeJSON = JSON_convert(category["income"])

def fetch_income_choices():
    return JSON_convert(temp_db._income_type)

def get_emoji_unicode(emoji_name):
    emoji = nextcord.utils.get(client.emojis, name=emoji_name)
    if emoji:
        return str(emoji)  # Converts the emoji to a string, which will be in the form of unicode
    return None

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
            category_list.append(f"{key} {value}")
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
            if is_followup:
                # Use followup if specified
                sent_msg = await ctx.followup.send(embed=embed, view=myview)
            else:
                # Use regular send otherwise
                sent_msg = await ctx.send(embed=embed, view=myview)

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
            text_input = TextInput(
                label=field_name,
                placeholder=field_options.get("placeholder", ""),
                required=field_options.get("required", True),
                style=field_options.get("style", TextInputStyle.short),
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
    def __init__(self, options: list[dict],max_values=1):
        """
        :param options: List of dictionaries containing option details.
                        Example:
                        [
                            {"label": "Option 1", "description": "Description 1", "value": "option_1", "emoji": "🚗"},
                            {"label": "Option 2", "description": "Description 2", "value": "option_2", "emoji": "👍"},
                        ]
        """
        super().__init__()
        self.selected_values = None
        # Create the dynamic Select menu
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
        
        # Assign the callback function to the dropdown
        self.dropdown.callback = self.dropdown_callback
        
        # Add the dropdown to the view
        self.add_item(self.dropdown)

    async def dropdown_callback(self, interaction: Interaction):
        # Get the selected value
        self.selected_values = self.dropdown.values
        selected_text = ", ".join(self.selected_values)  # You can support multiple selections if `max_values > 1`
        await interaction.response.send_message(f"You selected: {selected_text}", ephemeral=True)

class DropdownViewWithModal(View):
    def __init__(self, modal_callback,modal_title:str,modal_fields: list[dict],options: list[dict],max_values=1):
        super().__init__()
        self.modal_callback = modal_callback
        self.modal_title = modal_title
        self.modal_fields = modal_fields
        # Create the dropdown
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
        self.dropdown.callback = self.dropdown_callback
        self.add_item(self.dropdown)

    async def dropdown_callback(self, interaction: Interaction):
        # Get the selected value from the dropdown
        selected_option = self.dropdown.values[0]

        # Define and send the modal
        modal = DynamicModal(
            title=self.modal_title,
            fields=self.modal_fields,
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
            dynamic_button.callback = self.create_button_callback(button.get("label"))
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

    def create_button_callback(self, label):
        async def callback(interaction: Interaction):
            await self._handle_button_press(interaction, label)
        return callback

    async def _handle_button_press(self, interaction: Interaction, choice):
        """
        Handle button presses and call the callback function.

        Args:
            interaction (Interaction): The interaction object.
            choice (str): The button label that was pressed.
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
            # Defer the interaction response if not already done
            if not interaction.response.is_done():
                await interaction.response.defer()

            # Edit the message to disable buttons
            if self.message:
                await self.message.edit(view=self)
        except Exception as e:
            print(f"Edit message error: {e}")

        # Call the provided callback function with the choice
        try:
            await self.callback_function(interaction, choice)
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
            existing_guilds = json.load(f)  # Load existing data as a list
    except (FileNotFoundError, json.JSONDecodeError):
        list_guild_ids = []  # Initialize as empty if file doesn't exist or is invalid

    # Append the new guild ID if not already present
    if guild_id not in list_guild_ids:
        list_guild_ids.append(guild_id)

        # Save the updated list back to the JSON file
        with open("list_guild.json", "w") as f:
            json.dump({guild_id:guild_name}, f, indent=4)
    
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
    if guild.id in list_guild_ids:
        list_guild_ids.remove(guild.id)
        with open("list_guild.json", "w") as f:
            json.dump(list_guild_ids, f, indent=4)
        print(f"Updated guild list after removal.")

@client.slash_command(guild_ids=list_guild_ids,name="dropdown", description="Test a dropdown menu")
async def dropdown(interaction: Interaction):
    view = DropdownView()
    await interaction.response.send_message("Choose an option from the dropdown:", view=view, ephemeral=True)

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
    await EmbedNav(interaction,helpGuide,is_followup=True)

@client.slash_command(guild_ids=list_guild_ids, description="Show list of command with detail explanation")
async def menu(interaction:Interaction):
    await interaction.response.send_message(await CommandFunction.list_menu())

@client.slash_command(guild_ids=list_guild_ids, description="Register yourself with the bot")
async def register(
    interaction: Interaction,
    pin: str = SlashOption(description="Your pin for your account"),
    email: Optional[str] = SlashOption(description="Your email address", required=False, default=None)
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
    status,message = UserCommand.register_user(discord_id, username, pin, email)
    if status:
        buttons = [
        {"label": "Yes", "style": ButtonStyle.success, "custom_id": "yes_button"},
        {"label": "No", "style": ButtonStyle.danger, "custom_id": "no_button"}
        ]
        # Create the dynamic embed view
        embed_view = DynamicEmbedWithButtons(
            embed_title="Confirm Action",
            embed_description="Do you want to add template category?",
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

@client.slash_command(guild_ids=list_guild_ids, description="Show all categories (income or outcome)")
async def list_categories(interaction: Interaction, category_type: str = SlashOption(description="Choose category type", choices={"Income": "income", "Outcome": "outcome"}, required=False, default=None)):
    success, message = await CategoryCommand.get_all(category_type)
    # print(message)
    if success:
        await EmbedNav(interaction,message)
    else:
        await interaction.response.send_message(message)

@client.slash_command(guild_ids=list_guild_ids, description="Menu for add new outcome category")
@pin_required(client)
async def add_category(interaction:Interaction):
    async def handle_modal_submission(interaction:Interaction, inputs):
        # Combine dropdown and modal inputs
        await interaction.response.defer()
        emoticon = inputs.get('Emoticon')
        if emoticon:
            emoticon = emoji.emojize(emoticon, language='alias')
        status,message,data = await CategoryCommand.add(inputs.get('Name'),inputs.get('selected_option'),emoticon)
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


@client.slash_command(guild_ids=list_guild_ids, description="Add new income")
@pin_required(client)
async def add_income(interaction: Interaction,
                     amount: int = SlashOption(description='Amount'),
                     detail: Optional[str] = SlashOption(description='Detail of income', required=False, default=None),
                     date: Optional[str] = SlashOption(description='The date income was earned', default=None)):
    income_type_choices = fetch_income_choices() 

    async def process_selection(interaction: Interaction, selected_value: str):
        # Use the selected value for further processing
        print(selected_value)
        response_message = await CategoryCommand.add(selected_value, amount, detail, date)
        await interaction.followup.send(response_message)

    # Create the dynamic select view
    view = DynamicSelectView(options=income_type_choices, callback=process_selection)

    # Defer the response to avoid the timeout
    await interaction.response.defer()

    # Send the message with the dynamic select menu
    await interaction.followup.send("Select an income type:", view=view)

# @client.slash_command(guild_ids=list_guild_ids, description="Return list of income from a single day")
# async def daily_income(interaction:Interaction,date:Optional[str] = SlashOption(description='The date income was earn. Example => 30-08-2022',default=None)):
#     await interaction.response.send_message(await CommandFunction.get_daily_income(date))

# @client.slash_command(guild_ids=list_guild_ids, description="Return list of income from a month")
# async def monthly_income(interaction:Interaction,month:int = SlashOption(description='Month in number. Example => 6')):
#     await interaction.response.send_message(await CommandFunction.get_monthly_income(month))

# @client.slash_command(guild_ids=list_guild_ids, description="Transfer balance from one income type to another")
# async def transfer(interaction:Interaction,source:int = SlashOption(description='Source income category',choices = income_typeJSON),
#                     amount:int = SlashOption(description='Amount that want to be transfered'),
#                     target:int = SlashOption(description='Target income category',choices = income_typeJSON)):
#     await interaction.response.send_message(await CommandFunction.transfer(source,amount,target))

# @client.slash_command(guild_ids=list_guild_ids, description="Add new outcome")
# async def add_outcome(interaction:Interaction,outcome_type:int = SlashOption(description='Outcome category',choices=categoryJSON),
#                     income_type:int = SlashOption(description='Income category',choices=income_typeJSON),
#                     amount:int = SlashOption(description='Amount'),
#                     detail:Optional[str] = SlashOption(description='Detail of outcome',required=False, default=None),
#                     date:Optional[str] = SlashOption(description='The date outcome',default=None)):
#     await interaction.response.send_message(await CommandFunction.add_outcome(outcome_type,income_type,amount,detail,date))

# @client.slash_command(guild_ids=list_guild_ids, description="Return list of outcome from a single day")
# async def daily_outcome(interaction:Interaction,date:Optional[str] = SlashOption(description='The date outcome. Example => 30-08-2022',default=None)):
#     await interaction.response.send_message(await CommandFunction.get_daily_outcome(date))

# @client.slash_command(guild_ids=list_guild_ids, description="Return list of outcome from a month")
# async def monthly_outcome(interaction:Interaction, month:int = SlashOption(description='Month in number. Example => 6')):
#     title,list_data = await CommandFunction.get_monthly_outcome(month)
#     await interaction.response.send_message(title)
#     await EmbedNav(interaction,json.loads(json.dumps(list_data)))

# @client.slash_command(guild_ids=list_guild_ids, description="Return information about whether you overspend or not in specific month based on your budget plan")
# async def outcome_report(interaction:Interaction,month:int = SlashOption(description='Month in number. Example => 6')):
#     await interaction.response.send_message(await CommandFunction.get_outcome_report(month))

# @client.slash_command(guild_ids=list_guild_ids, description="Give detail information in a month about your income, outcome, and budget, group by income type")
# async def detail_budget(interaction:Interaction):
#     await interaction.response.send_message(await CommandFunction.detail_budget())

# @client.slash_command(guild_ids=list_guild_ids, description="Get latest outcome for the choosen category")
# async def specific_outcome(interaction:Interaction,amount:int = SlashOption(description='this is amount'),
#                     date:str = SlashOption(description='this is amount'),detail:str = SlashOption(description='this is amount',required=False)):
#     await interaction.response.send_message(f"Success {amount} {date} {detail}")

# @client.slash_command(guild_ids=list_guild_ids, description="Get latest outcome for the choosen category")
# async def add_budget_plan(interaction:Interaction,amount:int = SlashOption(description='this is amount'),
#                     date:str = SlashOption(description='this is amount'),detail:str = SlashOption(description='this is amount',required=False)):
#     await interaction.response.send_message(await CommandFunction.add_budget_plan(client,message))

# @client.slash_command(guild_ids=list_guild_ids, description="Get latest outcome for the choosen category")
# async def budget_plan(interaction:Interaction,amount:int = SlashOption(description='this is amount'),
#                     date:str = SlashOption(description='this is amount'),detail:str = SlashOption(description='this is amount',required=False)):
#     await interaction.response.send_message(await CommandFunction.get_monthly_budget_plan(client,message))

#     if message.content.startswith('!add_saving_plan'):
#         await message.channel.send(await CommandFunction.add_saving_plan(client,message))
        
#     if message.content.startswith('!add_limit_plan'):
#         await message.channel.send(await CommandFunction.add_limit_plan(client,message))
    
  # except Exception as e:
  #   exc_type, exc_obj, exc_tb = sys.exc_info()
  #   fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
  #   await message.channel.send(f":warning::warning::warning:\n```Something wrong! ->{str(e)} | {fname}```")

try:
    my_secret = ENV.TOKEN
    client.run(my_secret)
except HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system('kill 1')
    os.system("python restarter.py")