import discord
from discord.ext import commands
from function.Command import Command as CommandFunction
from _env import ENV

client = commands.Bot(command_prefix='!',intents=discord.Intents.all())
@client.event
async def on_ready():
    print("we have logged in successfully as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user or message.channel.name != 'bot-test':
        return
    print(message.content)
    if message.content.startswith("!help"):
        await message.channel.send(await CommandFunction.help())

    if message.content.startswith('!menu'):
        await message.channel.send(await CommandFunction.list_menu())

    if message.content.startswith('!add_category'):
        await message.channel.send(await CommandFunction.list_menu())

    if message.content.startswith('!add_outcome'):
        await message.channel.send(await CommandFunction.list_menu())

    if message.content.startswith('!add_income'):
        await message.channel.send(await CommandFunction.add_income(client,message))

    if message.content.startswith('!get_daily_expense'):
        await message.channel.send(await CommandFunction.list_menu())

    if message.content.startswith('!get_monthly_expense'):
        await message.channel.send(await CommandFunction.list_menu())

    if message.content.startswith('!get_saving'):
        await message.channel.send(await CommandFunction.list_menu())

    if message.content.startswith('!get_detail_saving'):
        await message.channel.send(await CommandFunction.list_menu())

client.run(ENV.TOKEN)