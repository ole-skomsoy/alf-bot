import discord as disc
from datetime import datetime
import jsonpickle
import random
from commands import *
from helpers import *


# how to 'repost'?
# 1. forward
# array of reactions, [🤭, 😂, 🤣, 😆], [🔥]
class test_bot(disc.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        message = await self.get_random_message()
        print(jsonpickle.encode(message)) #json pls 
    
    async def on_message(self, message):
        if message.author == self.user : return
        for c in commands:
            if message.content.startswith(c):
                await message.channel.send(commands[c])
                break
            elif message.content.startswith(1):
                await self.read_messages()
    
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🤫'),
            status=disc.Status.dnd)
        
    # 1. get random message in [created, now] (get batch)
    # 2. (todo) check if suitable
    #   - links: ['http://', 'https://'] contains message.content
    #   - pictures:
    #   - no link or pic: select other message
    async def get_random_message(self):
        # channel = self.get_channel(152136089367347200) #syria
        channel = self.get_channel(1365322546299273306) #bot-test-2
        around = datetime.fromtimestamp(random.randint(
                int(channel.created_at.timestamp()), 
                int(datetime.now().timestamp())))
    
        m = [message async for message in channel.history(around=around, limit=10)]
        for mi in m:
            print('------------------------------------------------------------------------')
            print(jsonpickle.encode(mi))
        return m[0]

# todo: move to main.py
def connect():
    intents = disc.Intents.default()
    intents.message_content = True
    client = test_bot(intents=intents)
    token = read_secret('discord_access_token')
    client.run(token)

connect()