import os, sys, json
from datetime import date
from typing import Any, List, Optional

from nextcord.ext import commands
from nextcord.errors import HTTPException
from nextcord import File, ButtonStyle, Embed, Color, SlashOption, Interaction, Intents,SelectOption, ui
from nextcord.ui import Button, View

from command.Command import Command as CommandFunction
from command.Category import Category as CategoryCommand

from temp_db import temp_db
from _env import ENV

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

category =  json.load(open("data\category.json"))
temp_db._category = category["outcome"]
categoryJSON = JSON_convert(category["outcome"])
temp_db._income_type = category["income"]
income_typeJSON = JSON_convert(category["income"])

def fetch_income_choices():
    print(45454544)
    return JSON_convert(temp_db._income_type)

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
            category_list.append(f"{key}: {value}")
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
                embed.add_field(name=category_name, value="\n".join(page_data), inline=inline)
                return embed
        
        # Update current_page_start to the next category's page range
        current_page_start += category_page_count

    return None  # If no data found for this page

async def EmbedNav(ctx, data, limit=7):
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

    async def next_callback(interaction):
        nonlocal currentPage, sent_msg
        currentPage += 1
        if currentPage >= total_pages:
            currentPage = 0  # Reset to the first page if we go beyond the total pages

        # Create the embed and send it
        embed = createHelpEmbed(data, currentPage, limit=limit, list_page=list_page)
        if embed:
            await sent_msg.edit(embed=embed, view=myview)
        await interaction.response.defer()

    async def previous_callback(interaction):
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
        sent_msg = await ctx.send(embed=embed, view=myview)


################################################################################################

@client.event
async def on_ready():
    # await client.sync_all_application_commands()
    print("we have logged in successfully as {0.user}".format(client))

@client.event
async def on_guild_join(guild):
    guild_id = guild.id
    guild_name = guild.name
    # Store the guild ID (you could save this to a database or file instead)
    list_guild_ids[guild_id] = guild_name
    print(f'Bot has joined a new guild: {guild_name} (ID: {guild_id})')

    # Save the updated dictionary to the JSON file
    with open("list_guild.json", "w") as f:
        json.dump(list_guild_ids, f, indent=4)
    
    # Check if the system channel exists and if the bot can send messages there
    if guild.system_channel is not None and guild.system_channel.permissions_for(guild.me).send_messages:
        await guild.system_channel.send(f'Thanks for adding me to {guild_name}!')
    else:
        print(f'Cannot send message in {guild_name}\'s system channel.')

@client.slash_command(guild_ids=list_guild_ids, description="Show list of command available to interact with")
async def help(interaction:Interaction):
    await EmbedNav(interaction,helpGuide)

@client.slash_command(guild_ids=list_guild_ids, description="Show list of command with detail explanation")
async def menu(interaction:Interaction):
    await interaction.response.send_message(await CommandFunction.list_menu())

@client.slash_command(guild_ids=list_guild_ids, description="Show all categories (income or outcome)")
async def list_categories(interaction: Interaction, category_type: str = SlashOption(description="Choose category type", choices={"Income": "income", "Outcome": "outcome"}, required=False, default=None)):
    success, message = await CategoryCommand.get_all(category_type)
    # print(message)
    if success:
        await EmbedNav(interaction,message)
    else:
        await interaction.response.send_message(message)

@client.slash_command(guild_ids=list_guild_ids, description="Menu for add new outcome category")
async def add_category(interaction:Interaction,
                    name:str = SlashOption(description='The name of category'),
                    category_type:str = SlashOption(description='Type of the category. ', choices={"Income": "Income", "Outcome": "Outcome"},required=True),
                    emoticon:str = SlashOption(description='Emoticon argument without semicolon. Example => smile', required=False,default=""),
                    ):
    status,message,data = await CategoryCommand.add(name,category_type,emoticon)
    await interaction.response.send_message(message)


@client.slash_command(guild_ids=list_guild_ids, description="Add new income")
async def add_income(interaction:Interaction,
                    amount:int = SlashOption(description='Amount'),
                    detail:Optional[str] = SlashOption(description='Detail of income',required=False, default=None),
                    date:Optional[str] = SlashOption(description='The date income was earn',default=None)):
    income_type_choices = fetch_income_choices()
    # Create a select menu with the dynamically loaded choices
    select_menu = ui.Select(
        placeholder="Choose an income type...",
        options=[
            SelectOption(label=key, value=value)
            for key,value in income_type_choices.items()
        ]
    )

    async def select_callback(interaction: Interaction):
        selected_value = select_menu.values[0]
        await interaction.response.edit_message(
            content=f"You selected income type {selected_value}. Now processing your request...",
            view=None
        )
    
    select_menu.callback = select_callback
    
    # Create a view to add the select menu
    view = ui.View()
    view.add_item(select_menu)

    await interaction.response.send_message("Select an income type:", view=view)
    # await interaction.response.send_message(await CommandFunction.add_income(income_type,amount,detail,date))

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