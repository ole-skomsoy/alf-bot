import discord as disc
from discord.ext import commands
import datetime
import collections
import requests
import jsonpickle
import random
import comics
from helpers import *
from lurke_rob_cog import *
from solo_queue_rob_cog import *
from riot_wrapper import *

class lurke_rob(commands.Bot):
    quote_reactions = ['😺','😸','😹','😻','😼','😽','🙀','😿','😾']
    tune_reactions = ['🔥','🙏','😍','😤']
    meme_reactions = ['🤭','😂','🤣','😆'] 
    
    async def setup_hook(self):
        await self.add_cog(lurke_rob_cog(self))
        await self.add_cog(solo_que_rob_cog(self))
        self.riot_wrapper = riot_wrapper()

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()

    async def on_message(self, message):
        await self.react_if_interesting_message(message)
    
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.watching, name='you'),
            status=disc.Status.dnd)
        
    async def post_random_messages(self, from_tune_channel, from_meme_channel, from_quote_api, from_comic_api):
        repost_channel = self.get_channel(read_secret('repost_channel'))
        
        if from_tune_channel:
            tune_channel = self.get_channel(read_secret('tune_channel'))
            tune_message = await self.get_random_message(tune_channel, 10)
            daily_tune_message = await self.forward_message(repost_channel, tune_message)
            await self.react_to_message(daily_tune_message, self.tune_reactions)
            
        if from_meme_channel:
            meme_channel = self.get_channel(read_secret('meme_channel'))
            meme_message = await self.get_random_message(meme_channel, 10)
            daily_meme_message = await self.forward_message(repost_channel, meme_message)
            await self.react_to_message(daily_meme_message, self.meme_reactions)
        
        if from_comic_api:
            daily_comic_message = await self.send_comic_message(repost_channel)
            await self.react_to_message(daily_comic_message, self.meme_reactions) 
            
        if from_quote_api:
            quote_message = self.get_random_quote()
            cat = self.get_random_cat()
            daily_quote_message = await self.send_quote_message(repost_channel, quote_message, cat)
            await self.react_to_message(daily_quote_message, self.quote_reactions)
    
    async def send_comic_message(self, channel):
        comic = comics.search('calvinandhobbes', date='random')
        comic.download()
        file = disc.File('./calvinandhobbes.png', filename="calvinandhobbes.png")
        return await channel.send(file=file)

    def get_random_quote(self):
        try:
            return requests.get(f'{read_secret('quote_api')}/random').json()[0]
        except:
            print('>>> error getting random quote')
    
    def get_random_cat(self):
        try:
            return requests.get(f'{read_secret('cat_api')}/cat?json=true').json()
        except:
            print('>>> error getting random cat')                      
        
    def test_dict(self):
        dict_1 = collections.defaultdict(dict)
        a = get_value(dict_1, 'A', 1)
        dict_1['A'][1] = 100
        dict_1['B'][2] = 200
        dict_1['C'][2] = 300
        b = get_value(dict_1, 'A', 1)
        c = 2
            
    async def check_in_game(self):
        lol_channel = self.get_channel(read_secret('lol_channel'))
        if not lol_channel : return
        accounts = riot_wrapper.get_account_dtos()
        
        for account in accounts:            
            summoner = riot_wrapper.get_summoner_dto(account)
            active_game = riot_wrapper.get_active_game(account, summoner)
            if active_game: 
                lol_message = await self.lol_notify(lol_channel, active_game)
                await self.react_to_message(lol_message, self.meme_reactions)
                return
            
            game_result = riot_wrapper.get_game_result(account, summoner)
            if game_result: 
                lol_message = await self.lol_notify(lol_channel, game_result)
                await self.react_to_message(lol_message, self.meme_reactions)
    
    async def lol_notify(self, channel, game_object):
        return await channel.send(embed=disc.Embed(title=game_object['title'], description=game_object['description'], color=game_object['color']))
           
    async def send_quote_message(self, channel, quote, cat):
        embed = disc.Embed(title=quote['a'], description=quote['q'], type='image')
        embed = embed.set_image(url=cat['url'])
        return await channel.send(embed=embed)

    async def get_random_message(self, channel, retry_count):
        around = datetime.datetime.fromtimestamp(random.randint(
                int(channel.created_at.timestamp()), 
                int(datetime.datetime.now().timestamp())))
        
        while retry_count > 0:
            messages = [message async for message in channel.history(around=around, limit=100)]
            random.shuffle(messages)
            
            for message in messages:
                if self.is_ext_content_message(message) : return message
                
            retry_count -= 1
            if retry_count <= 0 : raise Exception(f'>>> Failed to get random message ({retry_count} retries left)')

    def is_ext_content_message(self, message):
        suitable_sources = ['http://', 'https://']
        if any(source in message.content for source in suitable_sources):
                    return True
        for attachment in message.attachments:
            if (any(source in attachment.url for source in suitable_sources)):
                return True
        return False

    async def forward_message(self, channel, message):
        return await message.forward(channel)
    
    async def react_if_interesting_message(self, message):
        if message.author == self.user : return
        if not self.is_ext_content_message(message) : return
        
        if message.channel.id == read_secret('tune_channel'):
            await self.react_to_message(message, self.tune_reactions)
        
        if message.channel.id == read_secret('meme_channel'):
            await self.react_to_message(message, self.meme_reactions)
    
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
    await bot.post_random_messages(True, False, False, False)
    await ctx.response.send_message(content='member?', delete_after=3.0)

@bot.tree.command(name='lr_get_random_meme', description = "Get a random meme from the meme channel")
async def get_random_meme_command(ctx):
    await bot.post_random_messages(False, True, False, False)
    await ctx.response.send_message(content='member?', delete_after=3.0)

@bot.tree.command(name='lr_sync_commands', description = "Sync commands between client and server")
async def sync_commands(ctx):
    await bot.tree.sync()
    await ctx.response.send_message(content='syncing commands', delete_after=3.0)

token = read_secret('lurke_rob_access_token')
bot.run(token)