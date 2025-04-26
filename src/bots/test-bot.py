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
        self.daily_meme_id = 0
        self.daily_tune_id = 0
        await self.set_default_status()
        await self.post_daily_messages()
    
    async def on_message(self, message):
        if message.author == self.user : await self.react_to_message(message)
        for command in commands:
            if message.content.startswith(command):
                await message.channel.send(commands[command])
                break
    
    async def react_to_message(self, message):
        self.log(message)
        match message.id:
            case self.daily_meme_id:
                message.add_reaction(random.choice(['🤭','😂','🤣','😆']))
            case self.daily_tune_id:
                message.add_reaction(random.choice(['🔥','🙏','😍','😤']))
    
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🤫'),
            status=disc.Status.dnd)
        
    async def post_daily_messages(self):
        repost_channel = self.get_channel(read_secret('repost_channel'))
        
        meme_channel = self.get_channel(read_secret('meme_channel'))
        meme_message = await self.get_random_message(meme_channel, 10)
        self.log(meme_message)
        self.log(self.daily_meme_id)
        
        tune_channel = self.get_channel(read_secret('tune_channel'))
        tune_message = await self.get_random_message(tune_channel, 10)
        self.log(tune_channel)
        
        daily_meme_message = await self.post_message(repost_channel, meme_message)
        daily_tune_message = await self.post_message(repost_channel, tune_message)
        self.daily_meme_id = daily_meme_message.id
        self.daily_tune_id = daily_tune_message.id

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
        return await message.forward(channel)
        
    def log(self, object):
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