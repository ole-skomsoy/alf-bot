import discord as disc
from discord.ext import commands
from helpers import *

class spooky_rob(commands.Bot):
    
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.set_default_status()
        
    async def set_default_status(self):
        await self.change_presence(
            activity=disc.Activity(type=disc.ActivityType.listening, name='🙃'),
            status=disc.Status.dnd)
        
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