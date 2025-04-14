import discord as disc
from commands import *

intents = disc.Intents.default()
intents.message_content = True

client = disc.Client(intents=intents)

@client.event
async def on_ready():
     print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user : return
    for c in commands:
        if message.content.startswith(c):
            await message.channel.send(commands[c])
            break

def connect():
    client.run()

connect('token')