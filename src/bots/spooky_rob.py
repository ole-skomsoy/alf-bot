import discord as disc
from discord.ext import commands
import jsonpickle
import asyncio
import os, random
from helpers import *
from spooky_rob_cog import *

class spooky_rob(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(spooky_rob_cog(self))
        
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🙃'),
            status=disc.Status.dnd)
    
    async def on_voice_state_update(self, member, before, after):
        voice_channel = self.get_channel(read_secret('spooky_channel'))
        
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
    
    # /home/pi/code/alf-bot/src/bots/sounds
    async def play_random_sound(self):
        voice_client = disc.utils.get(self.voice_clients)
        if not voice_client or voice_client.is_playing() : return
        try:
            voice_client.play(disc.FFmpegPCMAudio(source=f'C:/Code/alf-bot/src/bots/sounds/sr_{random.randint(0,6)}.mp3'), after=lambda e: print('done', e))
            while voice_client.is_playing():
                await asyncio.sleep(1)
            voice_client.stop()
        except Exception as e:
                self.log(f"Error playing random sound: {e}")
    
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

token = read_secret('spooky_rob_access_token')
bot.run(token)