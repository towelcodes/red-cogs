from py3pin.Pinterest import Pinterest
from ..images import Image
from random import randint
import os, logging

logger = logging.getLogger("Pinterest Source")

logger.info("Attempting Pinterest login...")
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(os.path.dirname(__file__)))) # thanks stackoverflow <3
f = open(os.path.join(__location__, "pinterest_login.txt"))
buf: list[str] = f.readlines()
f.close()
pinterest = Pinterest(username=buf[0], email=buf[1], password=buf[2], cred_root=os.path.join(__location__, "pinterest_cred"))
pinterest.login()
logger.info(f"Logged into Pinterest: {pinterest}")

def pinterest_search(query: str) -> Image:
    logger.info(f"Searching Pinterest: {query}")
    result = pinterest.search(scope="pins", query=str, page_size=250)

    # pick a random result
    # TODO use a better method to find a good result
    selection = result[randint(0, len(result)-1)]
    url = selection["images"]["orig"]["url"]
    source = selection["link"]
    author = selection["pinner"]["username"]

    return Image(url, query.lower(), f"{author} (pinterest.com)", source)