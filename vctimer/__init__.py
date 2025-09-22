from redbot.core.commands import Bot
from .vctimer import VcTimer

async def setup(bot: Bot):
    await bot.add_cog(VcTimer(bot))
