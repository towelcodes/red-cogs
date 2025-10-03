from typing import List
from ..images import Image
import anime_api.apis as anime_apis
from enum import Enum
import requests
import random

def nekos_best(query: str) -> Image:
    i = anime_apis.NekosBest().get_random_images(
        image_type=anime_apis.nekos_best.ImageCategory[query.upper()],
        amount=1
    )[0]
    return Image(
        url=i.url, 
        category=query.lower(), 
        origin="nekos.best", 
        source=i.source_url
    )

def nekos_moe(tags: List[str], nsfw: bool) -> Image:
    i = anime_apis.NekosMoeAPI().search_images(nsfw=nsfw, tags=tags)[0]
    return Image(
        url=i.url, 
        category="".join(tags).lower(), 
        origin=f"nekos.moe{' [nsfw]' if nsfw else ''}", 
        source=f"https://nekos.moe/post/{i.id}"
    )

# this takes in a tag id
# to find them all GET https://api.nekosapi.com/v3/images/tags
# FIXME this is insecure as it appends the int to the query params as a string
def nekos_api(disp: str, tag: int, nsfw: bool) -> Image:
    res = requests.get(f"https://api.nekosapi.com/v3/images?tag={tag}&rating={'explicit' if nsfw else 'safe'}")
    res.raise_for_status()
    data = res.json()
    i = random.choice(data["items"])
    return Image(
        url=i["image_url"],
        category=disp,
        origin="nekosapi.com",
        source=i["source"]
    )

# rest in peace my favourite api :c
# def catboys() -> Image:
#     i = anime_apis.CatboysAPI().get_random_image()
#     print(f"url: {i.url} src: {i.source_url} artist: {i.artist}")
#     return Image(i.url, "catboy", "catboys.com", i.source_url)
