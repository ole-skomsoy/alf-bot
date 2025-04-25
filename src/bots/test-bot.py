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
        await self.post_daily_messages()
    
    async def on_message(self, message):
        if message.author == self.user : return
        for command in commands:
            if message.content.startswith(command):
                await message.channel.send(commands[command])
                break
    
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🤫'),
            status=disc.Status.dnd)
        
    async def post_daily_messages(self):
        repost_channel = self.get_channel(read_secret('repost_channel'))
        
        meme_channel = self.get_channel(read_secret('meme_channel'))
        meme_message = await self.get_random_message(meme_channel, 10)
        self.log(meme_message)
        
        tunes_channel = self.get_channel(read_secret('tunes_channel'))
        tunes_channel = await self.get_random_message(tunes_channel, 10)
        self.log(tunes_channel)
        
        await self.post_message(repost_channel, meme_message)
        await self.post_message(repost_channel, tunes_channel)

    async def get_random_message(self, channel, retry_count):
        around = datetime.fromtimestamp(random.randint(
                int(channel.created_at.timestamp()), 
                int(datetime.now().timestamp())))
        suitable_sources = ['http://', 'https://']
        
        while retry_count > 0:
            messages = [message async for message in channel.history(around=around, limit=100)]
            
            for message in [message async for message in channel.history(around=around, limit=100)]:
                if any(source in message.content for source in suitable_sources):
                    return message
                
                for attachment in message.attachments:
                    if (any(source in attachment.url for source in suitable_sources )):
                        return message
                    
            retry_count -= 1
            if retry_count <= 0 : raise Exception(f'>>> Failed to get random message ({retry_count} retries left)')
            return messages[0]

    async def post_message(self, channel, message):
        await message.forward(channel)
        
    async def log(self, object):
        print(jsonpickle.encode(object))
        print('----------------------------------------------------------------------------')
        
        
# todo: move to main.py
def connect():
    intents = disc.Intents.default()
    intents.message_content = True
    client = test_bot(intents=intents)
    token = read_secret('discord_access_token')
    client.run(token)

connect()