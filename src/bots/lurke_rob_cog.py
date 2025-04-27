from discord.ext import tasks, commands
import datetime
from helpers import *

class lurke_rob_cog(commands.Cog):
    def __init__(self, bot):
        self.lurke_rob = bot
        self.daily_scheduler.start()

    def cog_unload(self):
        self.daily_scheduler.cancel()

    @tasks.loop(time = datetime.time(hour=10, minute=0, tzinfo=datetime.timezone.utc))
    async def daily_scheduler(self):
        print('>>> posting daily messages')
        await self.lurke_rob.post_random_messages(True, True)