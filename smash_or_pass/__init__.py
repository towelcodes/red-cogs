from .smashorpass import SmashOrPassCog 

async def setup(bot):
    await bot.add_cog(SmashOrPassCog(bot))