from discord.ext import tasks, commands
from helpers import *

class solo_que_rob_cog(commands.Cog):
    def __init__(self, bot):
        self.solo_que_bot = bot
        self.check_in_game.start()
        self.check_game_result.start()

    def cog_unload(self):
        self.check_in_game.cancel()
        self.check_game_result.cancel()

    @tasks.loop(seconds=1)
    async def check_in_game(self):
        await self.solo_que_bot.check_in_game()
        
    @tasks.loop(seconds=5)
    async def check_game_result(self):
        pass
        # await self.solo_que_bot.check_game_result(True, True, True, True)