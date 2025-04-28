import discord as disc
from discord.ext import commands
import datetime
import requests
import jsonpickle
import random
from helpers import *
from lurke_rob_cog import *

class lurke_rob(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(lurke_rob_cog(self))

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        await self.post_random_messages(True, False, False)
    
    async def on_message(self, message):
        if message.author == self.user : pass
    
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🤫'),
            status=disc.Status.dnd)
        
    async def post_random_messages(self, from_quote_api, from_tune_channel, from_meme_channel):
        repost_channel = self.get_channel(read_secret('repost_channel'))
        
        if from_quote_api:
            quote_message = self.get_random_quote()
            cat = self.get_random_cat()
            daily_quote_message = await self.send_quote_message(repost_channel, quote_message, cat)
            await self.react_to_message(daily_quote_message, ['😺','😸','😹','😻','😼','😽','🙀','😿','😾'])
            
        if from_tune_channel:
            tune_channel = self.get_channel(read_secret('tune_channel'))
            tune_message = await self.get_random_message(tune_channel, 10)
            daily_tune_message = await self.forward_message(repost_channel, tune_message)
            await self.react_to_message(daily_tune_message, ['🔥','🙏','😍','😤'])
            
        if from_meme_channel:
            meme_channel = self.get_channel(read_secret('meme_channel'))
            meme_message = await self.get_random_message(meme_channel, 10)
            daily_meme_message = await self.forward_message(repost_channel, meme_message)
            await self.react_to_message(daily_meme_message, ['🤭','😂','🤣','😆'])

    def get_random_quote(self):
        try:
            return requests.get(f'{read_secret('quote_api')}/random').json()[0]
            # return {"q": "You are what you believe yourself to be.", "a": "Paulo Coelho", "h": "<blockquote>&ldquo;You are what you believe yourself to be.&rdquo; &mdash; <footer>Paulo Coelho</footer></blockquote>"}
        except:
            print('>>> error getting random quote')
    
    def get_random_cat(self):
        try:
            return requests.get(f'{read_secret('cat_api')}/cat?json=true').json()
        except:
            print('>>> error getting random cat')            
    
    async def send_quote_message(self, channel, quote, cat):
        embed = disc.Embed(title=quote['a'], description=quote['q'], type='image')
        embed = embed.set_image(url=cat['url'])
        return await channel.send(embed=embed)

    async def get_random_message(self, channel, retry_count):
        around = datetime.datetime.fromtimestamp(random.randint(
                int(channel.created_at.timestamp()), 
                int(datetime.datetime.now().timestamp())))
        suitable_sources = ['http://', 'https://']
        
        while retry_count > 0:
            messages = [message async for message in channel.history(around=around, limit=100)]
            random.shuffle(messages)

            for message in messages:
                if any(source in message.content for source in suitable_sources):
                    return message
                
                for attachment in message.attachments:
                    if (any(source in attachment.url for source in suitable_sources)):
                        return message
                    
            retry_count -= 1
            if retry_count <= 0 : raise Exception(f'>>> Failed to get random message ({retry_count} retries left)')

    async def forward_message(self, channel, message):
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

@bot.tree.command(name='lr_get_random_tune', description = "Get a random tune from the tune channel")
async def get_random_meme_command(ctx):
    await bot.post_random_messages(False, True, False)
    await ctx.response.send_message(content='member?', delete_after=3.0)

@bot.tree.command(name='lr_get_random_meme', description = "Get a random meme from the meme channel")
async def get_random_meme_command(ctx):
    await bot.post_random_messages(False, False, True)
    await ctx.response.send_message(content='member?', delete_after=3.0)

@bot.tree.command(name='lr_sync_commands', description = "Sync commands between client and server")
async def sync_commands(ctx):
    await bot.tree.sync()
    await ctx.response.send_message(content='syncing commands', delete_after=3.0)

token = read_secret('discord_access_token')
bot.run(token)