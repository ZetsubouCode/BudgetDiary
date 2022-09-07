import os
import discord
from discord.ext import commands
from function.Command import Command as CommandFunction
from temp_db import temp_db
from _env import ENV

list_command = ['!help','!menu','!add_category','!add_outcome','!add_income',
                '!add_budget_plan','!budget_plan','!add_saving_plan','!saving_plan',
                '!add_limit_plan','!limit_plan','!add_limit','!limit',
                '!daily_outcome', '!monthly_outcome', '!outcome_report', 
                '!saving','!monthly_income','!budget','!remaining_money','!transfer']

client = commands.Bot(command_prefix='!',intents=discord.Intents.all())
@client.event
async def on_ready():
    category = await CommandFunction.get_category()
    income_type = await CommandFunction.get_income_type()
    temp_db._category = category
    temp_db._income_type = income_type
    print("we have logged in successfully as {0.user}".format(client))

@client.event
async def on_message(message):
#   try:
    if message.author == client.user or message.channel.name != 'bot-test':
        return

    if message.content not in list_command and message.content.startswith('!'):
        await message.channel.send("There's no such command! Maybe you should use some `!help` :eye::lips::eye:")

    if message.content.startswith("!help"):
        await message.channel.send(await CommandFunction.help())

    if message.content.startswith('!menu'):
        await message.channel.send(await CommandFunction.list_menu())

    if message.content.startswith('!add_category'):
        await message.channel.send(await CommandFunction.add_category(client,message))

    if message.content.startswith('!add_outcome'):
        await message.channel.send(await CommandFunction.add_outcome(client,message))

    if message.content.startswith('!add_income'):
        await message.channel.send(await CommandFunction.add_income(client,message))

    if message.content.startswith('!add_budget_plan'):
        await message.channel.send(await CommandFunction.add_budget_plan(client,message))

    if message.content.startswith('!budget_plan'):
        await message.channel.send(await CommandFunction.get_monthly_budget_plan(client,message))

    if message.content.startswith('!add_saving_plan'):
        await message.channel.send(await CommandFunction.add_saving_plan(client,message))
        
    if message.content.startswith('!add_limit_plan'):
        await message.channel.send(await CommandFunction.add_limit_plan(client,message))

    if message.content.startswith('!daily_outcome'):
        await message.channel.send(await CommandFunction.get_daily_outcome(client,message))

    if message.content.startswith('!monthly_outcome'):
        await message.channel.send(await CommandFunction.get_monthly_outcome(client,message))

    if message.content.startswith('!outcome_report'):
        await message.channel.send(await CommandFunction.get_outcome_report(client,message))

    if message.content.startswith('!daily_income'):
        await message.channel.send(await CommandFunction.get_daily_income(client,message))

    if message.content.startswith('!monthly_income'):
        await message.channel.send(await CommandFunction.get_monthly_income(client,message))

    if message.content =='!budget':
        await message.channel.send(await CommandFunction.get_remaining_money(client,message))

    if message.content =='!transfer':
        await message.channel.send(await CommandFunction.transfer(client,message))
#   except Exception as e:
#     await message.channel.send(f":warning::warning::warning:\n```Something wrong! ->{str(e)}```")

try:
  my_secret = ENV.TOKEN
  client.run(my_secret)
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system('kill 1')
    os.system("python restarter.py")