from ..images import Image

# PLACEHOLDER = "https://cdn.discordapp.com/attachments/1104378531795963974/1122135129867952178/amon_gus.jpg"
PLACEHOLDER = "https://cdn.discordapp.com/attachments/1131214583336554496/1246592391750619177/IMG_2111.png?ex=665cf322&is=665ba1a2&hm=5b37692eb3935279ba125fc9cef3881e4363be55540096d4e4667913882f4c66&"
def placeholder() -> Image:
    return Image(PLACEHOLDER, "placeholder", "placeholder", None)