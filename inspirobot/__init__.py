from .inspirobot import InspiroBot

async def setup(bot):
    await bot.add_cog(InspiroBot(bot))
