import discord as disc
from discord.ext import commands
import datetime
import jsonpickle
from helpers import *

class spooky_rob(commands.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🙃'),
            status=disc.Status.dnd)
        
    async def on_voice_state_update(self, member, before, after):
        #self.log(before)
        #self.log(after)
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
            except disc.ClientException:
                self.log("Already connected to a voice channel")
            except Exception as e:
                self.log(f"Error connecting to voice channel: {e}")
        
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