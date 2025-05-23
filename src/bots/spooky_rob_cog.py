from discord.ext import tasks, commands
import datetime
import random
from helpers import *

class spooky_rob_cog(commands.Cog):
        
    def __init__(self, bot):
        self.spooky_rob = bot
        self.schedule_0.start()
        self.schedule_1.start()
        self.schedule_2.start()
        self.schedule_3.start()
        self.schedule_4.start()
        self.schedule_5.start()

    def cog_unload(self):
        self.schedule_0.cancel()

    @tasks.loop(seconds = 5.0)
    async def schedule_0(self):
        if random.randint(0,5) != 0 : return
        await self.spooky_rob.play_random_sound()
        
    @tasks.loop(seconds = 10.0)
    async def schedule_1(self):
        if random.randint(0,5) != 1 : return
        await self.spooky_rob.play_random_sound()
        
    @tasks.loop(seconds = 15.0)
    async def schedule_2(self):
        if random.randint(0,5) != 2 : return
        await self.spooky_rob.play_random_sound()
        
    @tasks.loop(seconds = 20.0)
    async def schedule_3(self):
        if random.randint(0,5) != 3 : return
        await self.spooky_rob.play_random_sound()
    
    @tasks.loop(seconds = 25.0)
    async def schedule_4(self):
        if random.randint(0,5) != 4 : return
        await self.spooky_rob.play_random_sound()
        
    @tasks.loop(seconds = 30.0)
    async def schedule_5(self):
        if random.randint(0,5) != 5 : return
        await self.spooky_rob.play_random_sound()