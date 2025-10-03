from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from discord import User
from redbot.core import Config

@dataclass
class Image:
    url: str
    category: str
    origin: str
    source: Optional[str]
    smashed: list[User] = field(default_factory=list, init=False)
    passed: list[User] = field(default_factory=list, init=False)

    def get_footer(self) -> str:
        return f"{self.category} via {self.origin}"

# moved here to avoid circular import
# there's probably a better way to do this
from .sources.anime import *
from .sources.placeholder import *
from .sources.list import *

PLACEHOLDER = "https://cdn.discordapp.com/attachments/1104378531795963974/1122135129867952178/amon_gus.jpg"
class ImageCategory(Enum):
    # there's definately a better way to do this (someone help me)
    async def call(self, conf: Config, serverid: int) -> Image:
        match self.value:
            case "waifu": return nekos_best("waifu")
            case "husbando": return nekos_best("husbando")
            case "neko": return nekos_best("neko")
            case "kitsune": return nekos_best("kitsune")
            case "loli": return nekos_api("loli", 10, False)
            case "jokes": return await jokes(conf, serverid)
            # case "catboy": return catboys()
            # case "demon slayer": return placeholder()
            # case "leng asian boys": return placeholder()
            # case "leng asian boys": return pinterest_search("asian boys")
            # case "leng asian boys": return image_search("asian boys")

    WAIFU = "waifu"
    HUSBANDO = "husbando"
    NEKO = "neko"
    KITSUNE = "kitsune"
    LOLI = "loli"
    JOKES = "jokes"
    # CATBOY = "catboy"
    # DEMON_SLAYER = "demon slayer"
    # LENG_ASIAN_BOYS = "leng asian boys"

# class ImageSource:
#     sources: List[Type] = []
#     def __call__(self, cls: Type):
#         self.sources.append(cls)

# TODO change to this abstract class ImageCategory
# class ImageCategory(ABC):
#     @abstractmethod
#     def name() -> str:
#         pass

#     @abstractmethod
#     async def fetch(self) -> Image:
#         pass
