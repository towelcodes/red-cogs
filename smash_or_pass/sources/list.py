from redbot.core import Config, commands
from ..images import Image
from typing import List, Tuple
from discord.ui import View, button, Button
from discord import ButtonStyle, Interaction, Message
import random

default_images: List[Tuple[str, str]] = [
    ("https://cdn.discordapp.com/attachments/1131214583336554496/1246595850986328156/image.png?ex=665cf65b&is=665ba4db&hm=8e395c5aaf105e0148cc0ae580803a167fa38d3c2c9001b01defd9e5f7dd9a49&", 
     "nimesh"),
    ("https://cdn.discordapp.com/attachments/1131214583336554496/1246597991360499722/IMG_1268.jpg?ex=665cf859&is=665ba6d9&hm=8d6a5ff5f7db7551f0d95a25fc24d6ea7684d6a941271f3453602bbb200cde71&",
     "yang"),
    ("https://cdn.discordapp.com/attachments/1131214583336554496/1246597992698351716/IMG_1270.jpg?ex=665cf85a&is=665ba6da&hm=3bbd00706c28bc10b51ac58616461faf283862c017c98c1bc3560fb970d106b2&",
     "yang"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246595944133427262/IMG_1081.jpg?ex=665cf671&is=665ba4f1&hm=3d05a50673aa597479325c364f9172b8a1e3b30d3f1c071d1efa20cb3b938f04&=&format=webp&width=512&height=683",
     "danji"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246596151726309487/IMG_0800.jpg?ex=665cf6a3&is=665ba523&hm=dafe3c49f998596f3eec58d36bff0a304a0061d41c634f7de0201123604624c7&=&format=webp&width=334&height=683",
     "nimesh"),
    ("https://cdn.discordapp.com/attachments/1131214583336554496/1246600923283853322/IMG_0230.jpg?ex=665cfb14&is=665ba994&hm=30f1fab0e64b6116684b16cd538624d857073b75023f2af4b16b4ae035d4253f&",
     "lucas"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246600884440268950/image.png?ex=665cfb0b&is=665ba98b&hm=35e718914243dcf73fb509e5eac106c6442d40c8e3757d653b4cee476fb0e62e&=&format=webp&quality=lossless",
     "danji + yang"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246600938882338879/image.png?ex=665cfb18&is=665ba998&hm=9e7972a7c6f65165fff6fb10d4ac156f153e6905350a5943ed7eecbe8a805392&=&format=webp&quality=lossless",
     "howard"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246601127894712412/image.png?ex=665cfb45&is=665ba9c5&hm=3b126b37c5f63c2bfacf8e3d974921360cec48853aeaa7693e4f67405d68b3ca&=&format=webp&quality=lossless",
     "shashank"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246601655990882334/image.png?ex=665cfbc3&is=665baa43&hm=9ebc73261a91b4b1c6ba6eb3877394c93bc5942e3572eceddc82807c01d855ba&=&format=webp&quality=lossless",
     "megamind"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246600677887709306/image.png?ex=665cfada&is=665ba95a&hm=33a2c99a2520a36a07f4bb222af7ca650d76482a2e5c8f40c7616d8420ce9ec0&=&format=webp&quality=lossless",
     "nonchalant deadhead #1"),
    ("https://cdn.discordapp.com/attachments/1131214583336554496/1246600595956039760/image.png?ex=665cfac6&is=665ba946&hm=35e51a5d45ee9c9b5e77b84721b226fa87a40a1d37817d58ac45da7e23350e2c&",
     "nonchalant dreadhead #2"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246603317291782184/IMG_6823.png?ex=665cfd4f&is=665babcf&hm=b217113f412a7393b996a94f62e88f35f9bd174b6cf921611305868110ba106d&=&format=webp&quality=lossless&width=316&height=683",
     "casual rizzler"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246603456014450738/IMG_6791.png?ex=665cfd70&is=665babf0&hm=fba78d7945a9cf98aaf167664ef561cacaa2aae77864c370681192fbcc2cd490&=&format=webp&quality=lossless&width=316&height=683",
     "..."),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246603793186164746/IMG_6731.jpg?ex=665cfdc1&is=665bac41&hm=696bb9b4bd339d1e7422598ad60906de030a6135e9485b2077405ee66da0f075&=&format=webp&width=512&height=683",
     "mogger"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246603812513251418/IMG_0231.jpg?ex=665cfdc5&is=665bac45&hm=b341cfd35a2d9db74f41e07f46cc180f1aacc19562fd07c06981ade3e92f4cc3&=&format=webp&width=512&height=683",
     "goon"),
    ("https://cdn.discordapp.com/attachments/1131214583336554496/1246604088901373962/photo.png?ex=665cfe07&is=665bac87&hm=b94f5f13156e0adc9ca526d726aec87f131372d0ed999d39ddd1039df883533e&",
     "..."),
    ("https://cdn.discordapp.com/attachments/1131214583336554496/1246606458695450696/IMG_1613.jpg?ex=665d003c&is=665baebc&hm=06b54534f3bbd39bd81aa9d1c5a9fe4e5da9328c311cdd7f55d95b99ffcd17f0&",
     "yang"),
    ("https://media.discordapp.net/attachments/1131214583336554496/1246607224370102372/IMG_6366.png?ex=665d00f3&is=665baf73&hm=3710b8cce94f0db799f06e92f1844ee445f22bbc2a7e64d9d46b6cd0e1cb5bf2&=&format=webp&quality=lossless&width=316&height=683",
     "bbc")
]

PLACEHOLDER = "https://cdn.discordapp.com/attachments/1131214583336554496/1246598039209250827/haha_not_allowed.png?ex=665cf865&is=665ba6e5&hm=9e68b7b2336aece1fa3772af06ff72f4043d1981512dcba3dffeba64ae13a08e&"
TRUSTED = [
    1130956708668252313,
    952834115533676545
]

# FIXME this may be inefficient (awaits config every time) -> check internal implementation to optimise
async def jokes(conf: Config, guildid: int) -> Image:
    if not guildid in TRUSTED:
        return Image(
            url=PLACEHOLDER,
            category="banned",
            origin="self",
            source=None
        )
    
    images: List[Tuple[str, str]] = await conf.guild_from_id(guildid).images()
    i = random.choice(images)
    return Image(
        url=i[0], 
        category=i[1], 
        origin="stupid", 
        source=None
    )

# will add a new image 
# FIXME not sure if this is thread safe (it probably is though)
async def add_new(conf: Config, guildid: int, label: str, url: str):
    images: List[Tuple[str, str]] = await conf.guild_from_id(guildid).images()
    images.append((url, label))
    await conf.guild_from_id(guildid).images.set(images)

class ImageVerifyView(View):
    def __init__(self, config: Config, guildid: int, label: str, img: str):
        super().__init__(timeout=None)
        self.config = config
        self.guildid = guildid
        self.label = label
        self.img = img

    @button(
        label="Approve",
        custom_id="approve",
        style=ButtonStyle.green
    )
    async def approve_button(self, interaction: Interaction, _: Button):
        await interaction.response.defer()
        v: List[Tuple[str, str]] = await self.config.guild_from_id(self.guildid).images()
        v.append((self.img, self.label))
        await self.config.guild_from_id(self.guildid).images.set(v)
        if interaction.message is None:
            await interaction.followup.send("Accepted submission (for some reason, I couldn't edit the original message)")
            return
        await interaction.followup.edit_message(interaction.message.id, content="**Submission accepted**", view=None)

    @button(
        label="Deny",
        custom_id="deny",
        style=ButtonStyle.red
    )
    async def deny_button(self, interaction: Interaction, _: Button):
        if interaction.message is None:
            await interaction.response.send_message("Submission denied (for some reason, I couldn't edit the original message)")
            return
        await interaction.response.edit_message(content="[Submission denied]", embed=None, view=None)