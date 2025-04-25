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
        message = await self.post_random_message()
        print(jsonpickle.encode(message)) #json pls 
    
    async def on_message(self, message):
        if message.author == self.user : return
        for command in commands:
            if message.content.startswith(command):
                await message.channel.send(commands[command])
                break
            elif message.content.startswith(1):
                await self.read_messages()
    
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🤫'),
            status=disc.Status.dnd)
        
    async def post_random_message(self):
        meme_message = await self.get_random_message(10)
        return meme_message
    
    async def get_random_message(self, retrycount):
        channel = self.get_channel(read_secret('meme_channel'))
        around = datetime.fromtimestamp(random.randint(
                int(channel.created_at.timestamp()), 
                int(datetime.now().timestamp())))
        suitable_content = ['http://', 'https://']
        
        try:
            messages = [message async for message in channel.history(around=around, limit=100)]
            for message in messages:
                if any(c in message for c in suitable_content):
                    return message
        except:
            retrycount -= 1
            raise Exception(f'>>> no suitable message found, retries left: {retrycount}')

# todo: move to main.py
def connect():
    intents = disc.Intents.default()
    intents.message_content = True
    client = test_bot(intents=intents)
    token = read_secret('discord_access_token')
    client.run(token)

connect()