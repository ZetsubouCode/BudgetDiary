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
    print(message)
    if message.content == "!help":
        await message.channel.send(await CommandFunction.help())

    if message.content == '!menu':
        await message.channel.send(await CommandFunction.list_menu())

client.run(ENV.TOKEN)