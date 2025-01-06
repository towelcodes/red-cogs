from redbot.core import commands, Config
from time import time
import platform, subprocess
import requests
from discord import Embed


class InspiroBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=612640209)
        default_global = {
            "host": "0.0.0.0",
            "login": "user",
            "passwd": "password"
        }
        self.config.register_global(**default_global)

    @commands.command()
    async def inspire(self, ctx):
        res = requests.get("https://inspirobot.me/api?generate=true")
        if res.status_code != 200:
            e = Embed(
                title="Error",
                description="Something went wrong :("
            )
            e.set_footer(f"status {res.status_code}")
            await ctx.send(embed=e)
            return
        e = Embed(
            title="how inspirational"
        )
        e.set_image(url=res.text)
        await ctx.send(embed=e)
