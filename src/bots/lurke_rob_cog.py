import discord as disc
from discord.ext import tasks, commands
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