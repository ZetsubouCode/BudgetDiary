import discord
from discord.ext import commands
from function.Command import Command as CommandFunction
from _env import ENV

list_command = ['!help','!menu','!add_category','!add_outcome','!add_income','!get_daily_expense', '!get_monthly_expense',
                '!get_saving','!get_detail_saving','!this_month_budget','!get_remaining_money']

client = commands.Bot(command_prefix='!',intents=discord.Intents.all())
@client.event
async def on_ready():
    print("we have logged in successfully as {0.user}".format(client))

@client.event
async def on_message(message):
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

    if message.content.startswith('!get_daily_expense'):
        await message.channel.send(await CommandFunction.get_daily_expense(client,message))

    if message.content.startswith('!get_monthly_expense'):
        await message.channel.send(await CommandFunction.get_monthly_expense(client,message))

    if message.content.startswith('!get_saving'):
        await message.channel.send(await CommandFunction.get_saving(client,message))

    if message.content.startswith('!get_detail_saving'):
        await message.channel.send(await CommandFunction.get_detail_saving(client,message))

    if message.content.startswith('!this_month_budget'):
        await message.channel.send(await CommandFunction.this_month_budget(client,message))

    if message.content.startswith('!get_remaining_money'):
        await message.channel.send(await CommandFunction.get_remaining_money(client,message))

client.run(ENV.TOKEN)