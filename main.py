import os, sys, json
from datetime import date
from typing import Any, List, Optional
from nextcord.ext import commands
import nextcord
from function.Command import Command as CommandFunction
from temp_db import temp_db
from _env import ENV
from nextcord import File, ButtonStyle, Embed, Color, SlashOption, Interaction
from nextcord.ui import Button, View

client = commands.Bot(command_prefix='!',intents=nextcord.Intents.all())
client.remove_command("help")
helpGuide = json.load(open("help.json"))

def JSON_convert(array:List[Any]):
        temp_json = {}
        for data in array:
            temp_json[data.name] = data.id
        return json.loads(json.dumps(temp_json))

category = CommandFunction.get_category()
income_type = CommandFunction.get_income_type()
temp_db._category = category
temp_db._income_type = income_type
categoryJSON = JSON_convert(category)
income_typeJSON = JSON_convert(income_type)

# create help embed using page number and json_file
def createHelpEmbed(json_file:dict, pageNum=0, inline=False):
    pageNum = (pageNum) % len(list(json_file))
    pageTitle = list(json_file)[pageNum]
    embed=Embed(color=0x0080ff, title=pageTitle)
    for key, val in json_file[pageTitle].items():
        embed.add_field(name=key, value=val, inline=inline)
        embed.set_footer(text=f"Page {pageNum+1} of {len(list(json_file))}")
    return embed

async def EmbedNav(ctx,json_file):
    currentPage = 0
    # functionality for buttons

    async def next_callback(interaction):
        nonlocal currentPage, sent_msg
        currentPage += 1
        await sent_msg.edit(embed=createHelpEmbed(json_file,currentPage), view=myview)
        await interaction.response.defer()

    async def previous_callback(interaction):
        nonlocal currentPage, sent_msg
        currentPage -= 1
        await sent_msg.edit(embed=createHelpEmbed(json_file,currentPage), view=myview)
        await interaction.response.defer()

    # add buttons to embed
    previousButton = Button(label="<", style=ButtonStyle.blurple)
    nextButton = Button(label=">", style=ButtonStyle.blurple)
    previousButton.callback = previous_callback
    nextButton.callback =  next_callback

    myview = View(timeout=180)
    myview.add_item(previousButton)
    myview.add_item(nextButton)
    sent_msg = await ctx.send(embed=createHelpEmbed(json_file,currentPage), view=myview)

async def Help(ctx):
    await EmbedNav(ctx,helpGuide)

@client.event
async def on_ready():
    print("we have logged in successfully as {0.user}".format(client))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Show list of command available to interact with")
async def help(interaction:Interaction):
    await Help(interaction)

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Show list of command with detail explanation")
async def menu(interaction:Interaction):
    await interaction.response.send_message(await CommandFunction.list_menu())

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Menu for add new outcome category")
async def add_category(interaction:Interaction, name:str = SlashOption(description='The name of category'),
                    emoticon:str = SlashOption(description='Emoticon argument without semicolon. Example => smile', required=False,default=None)):
    await interaction.response.send_message(await CommandFunction.add_category(name,emoticon))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Add new income")
async def add_income(interaction:Interaction,
                    income_type:int = SlashOption(description='ID of the income option',choices=income_typeJSON),
                    amount:int = SlashOption(description='Amount'),
                    detail:Optional[str] = SlashOption(description='Detail of income',required=False, default=None),
                    date:Optional[str] = SlashOption(description='The date income was earn',default=None)):
    await interaction.response.send_message(await CommandFunction.add_income(income_type,amount,detail,date))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Return list of income from a single day")
async def daily_income(interaction:Interaction,date:Optional[str] = SlashOption(description='The date income was earn. Example => 30-08-2022',default=None)):
    await interaction.response.send_message(await CommandFunction.get_daily_income(date))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Return list of income from a month")
async def monthly_income(interaction:Interaction,month:int = SlashOption(description='Month in number. Example => 6')):
    await interaction.response.send_message(await CommandFunction.get_monthly_income(month))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Transfer balance from one income type to another")
async def transfer(interaction:Interaction,source:int = SlashOption(description='Source income category',choices = income_typeJSON),
                    amount:int = SlashOption(description='Amount that want to be transfered'),
                    target:int = SlashOption(description='Target income category',choices = income_typeJSON)):
    await interaction.response.send_message(await CommandFunction.transfer(source,amount,target))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Add new outcome")
async def add_outcome(interaction:Interaction,outcome_type:int = SlashOption(description='Outcome category',choices=categoryJSON),
                    income_type:int = SlashOption(description='Income category',choices=income_typeJSON),
                    amount:int = SlashOption(description='Amount'),
                    detail:Optional[str] = SlashOption(description='Detail of outcome',required=False, default=None),
                    date:Optional[str] = SlashOption(description='The date outcome',default=None)):
    await interaction.response.send_message(await CommandFunction.add_outcome(outcome_type,income_type,amount,detail,date))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Return list of outcome from a single day")
async def daily_outcome(interaction:Interaction,date:Optional[str] = SlashOption(description='The date outcome. Example => 30-08-2022',default=None)):
    await interaction.response.send_message(await CommandFunction.get_daily_outcome(date))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Return list of outcome from a month")
async def monthly_outcome(interaction:Interaction, month:int = SlashOption(description='Month in number. Example => 6')):
    title,list_data = await CommandFunction.get_monthly_outcome(month)
    await interaction.response.send_message(title)
    await EmbedNav(interaction,json.loads(json.dumps(list_data)))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Return information about whether you overspend or not in specific month based on your budget plan")
async def outcome_report(interaction:Interaction,month:int = SlashOption(description='Month in number. Example => 6')):
    await interaction.response.send_message(await CommandFunction.get_outcome_report(month))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Give detail information in a month about your income, outcome, and budget, group by income type")
async def detail_budget(interaction:Interaction):
    await interaction.response.send_message(await CommandFunction.detail_budget())

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Get latest outcome for the choosen category")
async def specific_outcome(interaction:Interaction,amount:int = SlashOption(description='this is amount'),
                    date:str = SlashOption(description='this is amount'),detail:str = SlashOption(description='this is amount',required=False)):
    await interaction.response.send_message(f"Success {amount} {date} {detail}")

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Get latest outcome for the choosen category")
async def add_budget_plan(interaction:Interaction,amount:int = SlashOption(description='this is amount'),
                    date:str = SlashOption(description='this is amount'),detail:str = SlashOption(description='this is amount',required=False)):
    await interaction.response.send_message(await CommandFunction.add_budget_plan(client,message))

@client.slash_command(guild_ids=ENV.GUILD_ID, description="Get latest outcome for the choosen category")
async def budget_plan(interaction:Interaction,amount:int = SlashOption(description='this is amount'),
                    date:str = SlashOption(description='this is amount'),detail:str = SlashOption(description='this is amount',required=False)):
    await interaction.response.send_message(await CommandFunction.get_monthly_budget_plan(client,message))

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
except nextcord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system('kill 1')
    os.system("python restarter.py")