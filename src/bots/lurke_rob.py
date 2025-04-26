import discord as disc
from discord.ext import tasks, commands
from datetime import datetime
import jsonpickle
import random
from helpers import *


class lurke_rob_cog(commands.Cog):
    def __init__(self, bot):
        self.lurke_rob = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=1.0)
    async def printer(self):
        print(111)


class lurke_rob(disc.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        await self.post_daily_messages()
    
    async def on_message(self, message):
        if message.author == self.user : pass
    
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🤫'),
            status=disc.Status.dnd)
        
    async def post_daily_messages(self):
        repost_channel = self.get_channel(read_secret('repost_channel'))
        
        meme_channel = self.get_channel(read_secret('meme_channel'))
        meme_message = await self.get_random_message(meme_channel, 10)
        #self.log(meme_message)
        
        tune_channel = self.get_channel(read_secret('tune_channel'))
        tune_message = await self.get_random_message(tune_channel, 10)
        #self.log(tune_channel)
        
        daily_meme_message = await self.post_message(repost_channel, meme_message)
        await self.react_to_message(daily_meme_message, ['🤭','😂','🤣','😆'])
        
        daily_tune_message = await self.post_message(repost_channel, tune_message)
        await self.react_to_message(daily_tune_message, ['🔥','🙏','😍','😤'])

    async def get_random_message(self, channel, retry_count):
        around = datetime.fromtimestamp(random.randint(
                int(channel.created_at.timestamp()), 
                int(datetime.now().timestamp())))
        print(f'> date created: {channel.created_at} ({channel.created_at.timestamp()})')
        print(f'> date chosen: {around}')
        suitable_sources = ['http://', 'https://']
        
        while retry_count > 0:
            messages = [message async for message in channel.history(around=around, limit=100)]
            random.shuffle(messages)

            for message in messages:
                if any(source in message.content for source in suitable_sources):
                    return message
                
                for attachment in message.attachments:
                    if (any(source in attachment.url for source in suitable_sources )):
                        return message
                    
            retry_count -= 1
            if retry_count <= 0 : raise Exception(f'>>> Failed to get random message ({retry_count} retries left)')

    async def post_message(self, channel, message):
        return await message.forward(channel)
    
    async def react_to_message(self, message, reactions):
        await message.add_reaction(random.choice(reactions))

    def log(self, object):
        print(jsonpickle.encode(object))
        print('----------------------------------------------------------------------------')
        
        
# todo: move to main.py
def connect():
    intents = disc.Intents.default()
    intents.message_content = True
    client = lurke_rob(intents=intents)
    token = read_secret('discord_access_token')
    client.run(token)

connect()