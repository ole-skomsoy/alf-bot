import discord as disc
from datetime import datetime, date
import json
import random
from commands import *

class test_bot(disc.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        message = await self.get_random_message()
        print(message) #json pls 
    
    async def on_message(self, message):
        if message.author == self.user : return
        for c in commands:
            if message.content.startswith(c):
                await message.channel.send(commands[c])
                break
            elif message.content.startswith(1):
                await self.read_messages()
    
    async def set_default_status(self):
        await self.change_presence(activity=disc.Activity(type=disc.ActivityType.watching, name='🐶'))
        
    # 1. get random message in [created, now] (get batch)
    # 2. (todo) check if suitable
    #   - no: select other message (dont pop in case context for another message)
    # 3. (todo) check for missing context
    async def get_random_message(self):
        channel = self.get_channel(152136089367347200)
        around = datetime.fromtimestamp(random.randint(
                int(channel.created_at.timestamp()), 
                int(datetime.now().timestamp())))
    
        # messages = channel.history(around=around, limit=1)
        # numMessages = 0
        # find suitable message
        # async for message in messages:
        #     numMessages += 1
        #     print(message)
        #     j = json.dumps(message)
        
        m = [message async for message in channel.history(around=around, limit=1)][0]
        return m

def connect():
    intents = disc.Intents.default()
    intents.message_content = True
    client = test_bot(intents=intents)
    
    secrets_file = open('./src/secrets.json')
    secrets_content = secrets_file.read()
    token = json.loads(secrets_content)['discord_access_token']
    
    # self.client = client
    client.run(token)
    
connect()