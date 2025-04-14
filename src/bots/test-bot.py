import discord as disc
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

intents = disc.Intents.default()
intents.message_content = True

client = test_bot(intents=intents)
client.run('')
