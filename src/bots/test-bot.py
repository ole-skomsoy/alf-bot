import discord as disc
import json
from commands import *

class test_bot(disc.Client):
    async def on_ready(self):
         print(f'Logged in as {self.user}')    
    
    async def on_message(self, message):
        if message.author == self.user : return
        for c in commands:
            if message.content.startswith(c):
                await message.channel.send(commands[c])
                break

def connect():
    intents = disc.Intents.default()
    intents.message_content = True
    client = test_bot(intents=intents)
    
    secrets_file = open('./src/secrets.json')
    secrets_content = secrets_file.read()
    token = json.loads(secrets_content)['discord_access_token']
    
    client.run(token)

connect()