import discord as disc
from discord.ext import commands
import jsonpickle
import asyncio
from asyncio import run
import youtube_dl
import random
from helpers import *
from spooky_rob_cog import *

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(disc.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(disc.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class spooky_rob(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(spooky_rob_cog(self))
        
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.watching, name='you'),
            status=disc.Status.dnd)
    
    async def set_listening_status(self, track):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.playing, name=track),
            status=disc.Status.dnd)
    
    async def on_voice_state_update(self, member, before, after):
        voice_channel = self.get_channel(read_secret('spooky_channel'))
        if member.id == read_secret('spooky_rob_id') and not after.channel:
                await self.set_default_status()
        
        if len(voice_channel.members) == 1 and voice_channel.members[0].id == read_secret('spooky_rob_id'):
            try:
                voice_client = disc.utils.get(self.voice_clients)
                await voice_client.disconnect()
            except Exception as e:
                self.log(f"Error disconnecting fRom voice channel: {e}")
        
        if after.channel and after.channel.id == read_secret('spooky_channel'):
            try:
                await voice_channel.connect()
                await self.play_random_sound()
            except disc.ClientException:
                self.log("Already connected to a voice channel")
            except Exception as e:
                self.log(f"Error connecting to voice channel: {e}")
    
    async def play_random_sound(self):
        voice_client = disc.utils.get(self.voice_clients)
        if not voice_client or voice_client.is_playing() : return
        try:
            # voice_client.play(disc.FFmpegPCMAudio(source=f'C:/Code/alf-bot/src/bots/sounds/sr_{random.randint(0,25)}.mp3'), after=lambda e: print('done', e))
            voice_client.play(disc.FFmpegPCMAudio(source=f'/home/pi/code/alf-bot/src/bots/sounds/sr_{random.randint(0,25)}.mp3'), after=lambda e: print('done', e))
            while voice_client.is_playing():
                await asyncio.sleep(1)
            voice_client.stop()
        except Exception as e:
                self.log(f"Error playing random sound: {e}")
    
    async def play_yt(self, url):
        voice_client = disc.utils.get(self.voice_clients)
        if not voice_client : return
        if voice_client.is_playing():
            voice_client.stop()
        
        player = await YTDLSource.from_url(url, loop=self.loop)
        await self.set_listening_status(player.title)
        voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else run(self.set_default_status()))
    
    async def stream_yt(self, url):
        voice_client = disc.utils.get(self.voice_clients)
        if not voice_client : return
        if voice_client.is_playing():
            voice_client.stop()
        
        player = await YTDLSource.from_url(url, loop=self.loop, stream=True)
        await self.set_listening_status(player.title)
        voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else run(self.set_default_status()))

    
    def sr_stop_audio(self):
        voice_client = disc.utils.get(self.voice_clients)
        if not voice_client or not voice_client.is_playing() : return
        voice_client.stop()
        
    
    def log(self, object):
        print(jsonpickle.encode(object))
        print('----------------------------------------------------------------------------')
        
        
intents = disc.Intents.default()
intents.message_content = True

# dont bother trying to change the command prefix
bot = spooky_rob(command_prefix='/', intents=intents)

@bot.tree.command(name='sr_sync_commands', description = "Sync commands between client and server")
async def sync_commands(ctx):
    await bot.tree.sync()
    await ctx.response.send_message(content='syncing commands', delete_after=3.0)

@bot.tree.command(name='sr_play', description = "Play audio from youtube")
async def sr_play_yt(ctx, url:str):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt(url)
    
@bot.tree.command(name='sr_stream', description = "Stream audio from youtube")
async def sr_play_yt(ctx, url:str):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.stream_yt(url)
    
@bot.tree.command(name='sr_stop', description = "Stop the currently playing audio")
async def sr_stop_audio(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=1.0)
    bot.sr_stop_audio()
    
@bot.tree.command(name='sr_cassette_1', description = "Play cassette #1")
async def sr_play_yt(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt('https://www.youtube.com/watch?v=qWpt-_Dk4OA&ab_channel=GabeCastro')

@bot.tree.command(name='sr_cassette_2', description = "Play cassette #2")
async def sr_play_yt(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt('https://www.youtube.com/watch?v=M7y2YHa9Jcg&list=PLFcrLZcXktso9Jz-wWRaYwwkxjPLOtwIq&index=2&ab_channel=GabeCastro')
    
@bot.tree.command(name='sr_cassette_3', description = "Play cassette #3")
async def sr_play_yt(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt('https://www.youtube.com/watch?v=HJBHsdVp75M&list=PLFcrLZcXktso9Jz-wWRaYwwkxjPLOtwIq&index=3&ab_channel=GabeCastro')
    
@bot.tree.command(name='sr_cassette_4', description = "Play cassette #4")
async def sr_play_yt(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt('https://www.youtube.com/watch?v=SfkfRW_ufMo&list=PLFcrLZcXktso9Jz-wWRaYwwkxjPLOtwIq&index=4&ab_channel=GabeCastro')
    
@bot.tree.command(name='sr_cassette_5', description = "Play cassette #5")
async def sr_play_yt(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt('https://www.youtube.com/watch?v=Aj4YGcy5Yk4&list=PLFcrLZcXktso9Jz-wWRaYwwkxjPLOtwIq&index=5&ab_channel=GabeCastro')

@bot.tree.command(name='sr_cassette_6', description = "Play cassette #6")
async def sr_play_yt(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt('https://www.youtube.com/watch?v=3iONFj3dTbI&list=PLFcrLZcXktso9Jz-wWRaYwwkxjPLOtwIq&index=6&ab_channel=GabeCastro')
    
@bot.tree.command(name='sr_cassette_7', description = "Play cassette #7")
async def sr_play_yt(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt('https://www.youtube.com/watch?v=MKKLwahE_J8&list=PLFcrLZcXktso9Jz-wWRaYwwkxjPLOtwIq&index=7&ab_channel=GabeCastro')

@bot.tree.command(name='sr_cassette_8', description = "Play cassette #8")
async def sr_play_yt(ctx):
    await ctx.response.send_message(content='Gimme a moment...', delete_after=5.0)
    await bot.play_yt('https://www.youtube.com/watch?v=u22lVpauhRI&list=PLFcrLZcXktso9Jz-wWRaYwwkxjPLOtwIq&index=8&ab_channel=GabeCastro')

token = read_secret('spooky_rob_access_token')
bot.run(token)