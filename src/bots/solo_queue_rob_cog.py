from discord.ext import tasks, commands

class solo_que_rob_cog(commands.Cog):
    def __init__(self, bot):
        self.solo_que_bot = bot
        self.check_in_game.start()

    def cog_unload(self):
        self.check_in_game.cancel()

    @tasks.loop(seconds=1)
    async def check_in_game(self):
        await self.solo_que_bot.check_in_game()