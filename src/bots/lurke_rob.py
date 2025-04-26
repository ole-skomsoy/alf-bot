import discord as disc
from discord.ext import commands
from datetime import datetime
import jsonpickle
import random
from helpers import *
from lurke_rob_cog import *

class lurke_rob(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(lurke_rob_cog(self))
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        await self.tree.sync()
    
    async def on_message(self, message):
        if message.author == self.user : pass
    
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🤫'),
            status=disc.Status.dnd)
        
    async def post_random_messages(self, from_meme_channel, from_tune_channel):
        repost_channel = self.get_channel(read_secret('repost_channel'))
        
        if from_meme_channel:
            meme_channel = self.get_channel(read_secret('meme_channel'))
            meme_message = await self.get_random_message(meme_channel, 10)
            daily_meme_message = await self.post_message(repost_channel, meme_message)
            await self.react_to_message(daily_meme_message, ['🤭','😂','🤣','😆'])
        
        if from_tune_channel:
            tune_channel = self.get_channel(read_secret('tune_channel'))
            tune_message = await self.get_random_message(tune_channel, 10)
            daily_tune_message = await self.post_message(repost_channel, tune_message)
            await self.react_to_message(daily_tune_message, ['🔥','🙏','😍','😤'])

    async def get_random_message(self, channel, retry_count):
        around = datetime.fromtimestamp(random.randint(
                int(channel.created_at.timestamp()), 
                int(datetime.now().timestamp())))
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


intents = disc.Intents.default()
intents.message_content = True

# dont bother trying to change the command prefix
bot = lurke_rob(command_prefix='/', intents=intents)

@bot.tree.command(name='get_random_meme', description = "Get a random meme from the meme channel")
async def get_random_meme_command(ctx):
    ctx.post_random_messages(True, False)
    
@bot.tree.command(name='get_random_meme2', description = "Get a random tune from the tune channel")
async def get_random_meme_command(ctx):
    ctx.post_random_messages(False, True)

token = read_secret('discord_access_token')
bot.run(token)

# bot.tree.sync()

# setup()