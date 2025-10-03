import discord
from redbot.core import commands
from redbot.core.bot import Red
from discord import Embed, ButtonStyle, Interaction, Member, User, Emoji, SelectOption, Attachment, TextChannel
from discord.ui import Button, View, button, Select, select
from discord.abc import Messageable
from redbot.core.commands import Context
from random import randint
from .images import *
from .sources.list import TRUSTED, default_images, add_new, ImageVerifyView
import logging


class SmashOrPassCog(commands.Cog):
    def __init__(self, bot: Red):
        self.logger = logging.getLogger("SmashOrPassCog")
        self.bot = bot

        # setup default custom images
        self.config = Config.get_conf(self, identifier=999478265, force_registration=True)
        default_guild = {
            "images": default_images,
            "mod_channel": 0
        }
        self.config.register_guild(**default_guild)

    @commands.command()
    async def smashorpass(self, ctx: Context):
        e = Embed(
            color=0xEE2222,
            title="Smash or Pass",
            description="Select a category"
        )
        v = SmashOrPassInitView(self.config, ctx.guild.id if not ctx.guild is None else 0)
        await ctx.send(embed=e, view=v)
        
    # TODO work out how to make a proper alias
    @commands.command()
    async def sop(self, ctx: Context):
        await self.smashorpass(ctx)

    @commands.guild_only()
    @commands.command()
    async def suggest(self, ctx: Context, label: str, image: Attachment):
        assert ctx.guild is not None
        if not ctx.guild.id in TRUSTED:
            await ctx.reply("Not supported in this server (contact owner if you think this is a mistake)")
            return
        e = Embed(title="SOP image submission", description=f"From: {ctx.author.mention}").set_image(url=image.url)
        view = ImageVerifyView(self.config, ctx.guild.id, label, image.url)
        chan = self.bot.get_channel(await self.config.guild(ctx.guild).mod_channel())
        if type(chan) == TextChannel:
            await chan.send(embed=e, view=view)
        else:
            await self.bot.send_to_owners("tried to send to mod channel, but it was not Messagable" if chan is not None else "", embed=e, view=view)
        await ctx.reply("Your submission was sent to the admins for review")

    @commands.guild_only()
    @commands.admin()
    @commands.command()
    async def set_review_channel(self, ctx: Context, channel: TextChannel):
        assert ctx.guild is not None
        await self.config.guild(ctx.guild).mod_channel.set(channel.id)
        await ctx.reply("done")

    @commands.guild_only()
    @commands.admin()
    @commands.command()
    async def get_review_channel(self, ctx: Context):
        assert ctx.guild is not None
        chan = await self.config.guild(ctx.guild).mod_channel()
        await ctx.reply(f"<#{chan}> ({chan})")
    
    # WARNING this commands assumed all checks have passed and the thing is valid
    # should not be exposed to users
    @commands.guild_only()
    @commands.admin()
    @commands.command()
    async def add_img(self, ctx: Context, label: str, url: str):
        assert ctx.guild is not None
        if not ctx.guild.id in TRUSTED:
            await ctx.reply("Not supported in this server (contact owner if you think this is a mistake)")
            return
        await add_new(self.config, ctx.guild.id, label, url)
        await ctx.reply("done")

        
    @commands.guild_only()
    @commands.admin()
    @commands.command()
    async def list_img(self, ctx: Context):
        assert ctx.guild is not None
        if not ctx.guild.id in TRUSTED:
            await ctx.reply("Not supported in this server (contact owner if you think this is a mistake)")
            return
        data = await self.config.guild(ctx.guild).images()
        print(f"DATA :: {data} :: END")

        # split up the data so we don't reach char limit
        split: List[List[Tuple[str, str]]] = []
        b = []
        for v in data:
            b.append(v)
            if len(b) > 9:
                split.append(b)
                b = []
        # don't forget any data at the end
        split.append(b)

        print(f"\n\n{split}\n\n {len(split)}\n\n {split[0]}")

        embeds: List[Embed] = []
        for v in split:
            print(f"\n\n{v}")
            s = ""
            for img in v:
                s += f"[{img[1]}]({img[0]})\n"
            embeds.append(Embed(
                title="User Submitted Images", 
                description=s,
                ))
        
        for e in embeds:
            await ctx.reply(embed=e)

    # can match either name OR url
    @commands.guild_only()
    @commands.admin()
    @commands.command()
    async def remove_img(self, ctx: Context, kw: str):
        assert ctx.guild is not None
        if not ctx.guild.id in TRUSTED:
            await ctx.reply("Not supported in this server (contact owner if you think this is a mistake)")
            return
        found = False
        async with ctx.typing():
            data: List[Tuple[str, str]] = await self.config.guild(ctx.guild).images()
            for i, v in enumerate(data):
                if v[0] == kw or v[1] == kw:
                    found = True
                    await ctx.reply(f"removed: {data.pop(i)}")
            await self.config.guild(ctx.guild).images.set(data)
        if not found:
            await ctx.reply("keyword not found (try [pre]list_img)")
        # apply changes

    @commands.guild_only()
    @commands.admin()
    @commands.command()
    async def query_img(self, ctx: Context, kw: str):
        assert ctx.guild is not None
        if not ctx.guild.id in TRUSTED:
            await ctx.reply("Not supported in this server (contact owner if you think this is a mistake)")
            return
        found = False
        async with ctx.typing():
            data: List[Tuple[str, str]] = await self.config.guild(ctx.guild).images()
            for v in data:
                if v[0] == kw or v[1] == kw:
                    found = True
                    await ctx.reply(f"found: {v}")
        if not found:
            await ctx.reply("keyword not found (try [pre]list_img)")

class SmashOrPassView(View):
    def __init__(self, images: list[Image], image_categories: list[ImageCategory], config: Config, serverid: int):
        self.logger = logging.getLogger("SmashOrPassView")
        self.logger.info(f"init with IMAGES {images} CATEGORIES {image_categories}")
        self.config = config
        self.serverid = serverid

        super().__init__(timeout=None)

        self.images: list[Image] = images
        self.img_index: int = 0
        self.categories: list[ImageCategory] = image_categories

        # TODO current: sort out init message instead, call this from the init message, make sure category selector works

        self.smashed: list[User] = []
        self.passed: list[User] = []

        self.source_btn: Button = Button(
            label="Source",
            emoji="🔗",
            url=self.images[self.img_index].source
        )
        self.add_item(self.source_btn)

        options = [
            SelectOption(label="Waifu", default=ImageCategory.WAIFU in self.categories),
            SelectOption(label="Husbando", default=ImageCategory.HUSBANDO in self.categories),
            SelectOption(label="Neko", default=ImageCategory.NEKO in self.categories),
            SelectOption(label="Kitsune", default=ImageCategory.KITSUNE in self.categories),
            SelectOption(label="Loli", default=ImageCategory.LOLI in self.categories),
            SelectOption(label="Jokes", default=ImageCategory.JOKES in self.categories),
            # SelectOption(label="Catboy", default=self.categories.__contains__(ImageCategory.CATBOY)),
            # SelectOption(label="Demon Slayer", default=self.categories.__contains__(ImageCategory.DEMON_SLAYER)),
            # SelectOption(label="Leng Asian Boys", default=self.categories.__contains__(ImageCategory.LENG_ASIAN_BOYS)),
        ]
        
        self.select = Select(custom_id="categories", options=options, min_values=1, max_values=len(ImageCategory._member_names_), row=2, placeholder="Categories")
        self.select.callback = self.category_sel
        self.add_item(self.select)

    async def __build_new_view(self, interaction: Interaction, categories: list[ImageCategory]):
        init_cat = categories[randint(0, len(categories)-1)]
        init_img = await init_cat.call(self.config, interaction.guild_id or 0)
        e = Embed(color=0xEE2222, title="Smash or Pass") \
            .set_image(url=init_img.url) \
            .set_footer(text=init_img.get_footer())
        e.image.url = init_img.url
        self.logger.info(f"inital image: {init_img}")
        self.logger.info(f"categories: {categories}")
        v = SmashOrPassView([init_img], categories, self.config, self.serverid)
        self.logger.info(f"sending message send request")
        self.logger.info(f"embed: {e}")
        self.logger.info(f"view: {v}")
        await interaction.response.send_message(embed=e, view=v)

    def __update_source(self):
        if self.source_btn:
            self.remove_item(self.source_btn)
        self.source_btn = Button(
            label="Source",
            emoji="🔗",
            url=self.images[self.img_index].source
        )
        self.add_item(self.source_btn)

    # build an embed to senk
    async def __build_embed(self) -> Embed:
        i: Image

        if (self.img_index<0):
            self.logger.warn("img_index below 0, resetting")
            self.img_index = 0

        try:
            i = self.images[self.img_index]
        except IndexError:
            # append more images to the list
            category: ImageCategory = self.categories[randint(0, len(self.categories)-1)]
            self.images.append(await category.call(self.config, self.serverid))
            i = self.images[self.img_index] # TODO if the index is wrong for some reason this will fail! more checks needed
        
        self.__update_source()

        # FIXME this really shouldn't use the variables on self
        self.smashed = i.smashed
        self.passed = i.passed

        e = Embed(color=0xEE2222, title="Smash or Pass") \
            .set_image(url=i.url) \
            .set_footer(text=f"{i.get_footer()} | page {self.img_index}") 
        e.image.url = i.url
        return self.__gen_fields(e)


    # regen the fields in the embed
    def __gen_fields(self, embed: Embed) -> Embed:
        if len(self.smashed)==0 and len(self.passed)==0:
            return embed.clear_fields()

        e = embed.clear_fields() \
            .add_field(name="Smashed", value="") \
            .add_field(name="Passed", value="")

        # generate smashed list
        buf = ""
        for user in self.smashed:
            buf += f"{user.mention}\n"
        e.set_field_at(0, name="Smashed", value=buf)

        # generate passed list
        buf = ""
        for user in self.passed:
            buf += f"{user.mention}\n"
        e.set_field_at(1, name="Passed", value=buf)

        return e

    @button(
        custom_id="smash",
        row=0,
        label="Smash", 
        style=ButtonStyle.green)
    async def smash_btn(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        
        if interaction.message is None:
            await interaction.followup.send("Error occurred (interaction has no message)")
            return
        
        user = interaction.client.get_user(interaction.user.id)

        if user is None:
            await interaction.followup.send("Error occurred (user not found)")
            return

        e = interaction.message.embeds[0]
        smashed = self.images[self.img_index].smashed
        passed = self.images[self.img_index].passed
        if smashed.__contains__(user):
            smashed.remove(user)
        else:
            smashed.append(user)
            if passed.__contains__(user):
                passed.remove(user)
        await interaction.followup.edit_message(interaction.message.id, embed=self.__gen_fields(e))

    @button(
        custom_id="pass",
        row=0,
        label="Pass", 
        style=ButtonStyle.red)
    async def pass_btn(self, interaction: Interaction, _):
        await interaction.response.defer()

        if interaction.message is None:
            await interaction.followup.send("Error occured (interaction has no message)")
            return
        
        user = interaction.client.get_user(interaction.user.id)

        if user is None:
            await interaction.followup.send("Error occurred (user not found)")
            return
        
        e = interaction.message.embeds[0]
        smashed = self.images[self.img_index].smashed
        passed = self.images[self.img_index].passed
        if passed.__contains__(user):
            passed.remove(user)
        else:
            passed.append(user)
            if smashed.__contains__(user):
                smashed.remove(user)
        await interaction.followup.edit_message(interaction.message.id, embed=self.__gen_fields(e))

    @button(
        custom_id="back",
        row=1,
        emoji="⏪", 
        style=ButtonStyle.blurple)
    async def back_btn(self, interaction: Interaction, _):
        await interaction.response.defer()
        if interaction.message is None:
            await interaction.followup.send("Error occured (interaction has no message)")
            return

        self.img_index = 0
        await interaction.followup.edit_message(interaction.message.id, embed=await self.__build_embed(), view=self)

    @button(
        custom_id="prev",
        row=1,
        emoji="⬅️", 
        style=ButtonStyle.blurple)
    async def prev_btn(self, interaction: Interaction, _):
        await interaction.response.defer()
        if interaction.message is None:
            await interaction.followup.send("Error occured (interaction has no message)")
            return

        self.img_index -= 1
        if self.img_index < 0:
            self.img_index = 0
        await interaction.followup.edit_message(interaction.message.id, embed=await self.__build_embed(), view=self)

    @button(
        custom_id="next",
        row=1,
        emoji="➡️", 
        style=ButtonStyle.blurple)
    async def next_btn(self, interaction: Interaction, _):
        await interaction.response.defer()
        if interaction.message is None:
            await interaction.followup.send("Error occured (interaction has no message)")
            return

        self.img_index += 1
        await interaction.followup.edit_message(interaction.message.id, embed=await self.__build_embed(), view=self)

    @button(
        custom_id="end",
        row=1,
        emoji="⏩", 
        style=ButtonStyle.blurple)
    async def end_btn(self, interaction: Interaction, _):
        await interaction.response.defer()
        if interaction.message is None:
            await interaction.followup.send("Error occured (interaction has no message)")
            return

        self.img_index = len(self.images)-1
        await interaction.followup.edit_message(interaction.message.id, embed=await self.__build_embed(), view=self)

    @button(
        custom_id="new",
        row=1,
        label="New",
        style=ButtonStyle.blurple)
    async def new_btn(self, interaction: Interaction, _):
        e = Embed(
            color=0xEE2222,
            title="Smash or Pass",
            description="Select a category"
        )
        v = SmashOrPassInitView(self.config, self.serverid)
        ctx = Context(
            interaction=interaction,
            message=interaction.message,
            bot=interaction.client,
            view=self
        )
        await ctx.send(embed=e, view=v)

    async def category_sel(self, interaction: Interaction):
        selected = self.select.values
        # hacky way to do this but idc it works
        categories: list[ImageCategory] = []
        for sel in selected:
            categories.append(ImageCategory[sel.upper().replace(" ", "_").replace("-", "_")])
        await self.__build_new_view(interaction, categories)
        self.logger.info(f"categories selected: {categories}")
        init_category = categories[randint(0, len(categories)-1)]
        self.logger.info(f"inital category: {init_category.value}")
        self.logger.info(f"inital image: {await init_category.call(self.config, self.serverid)}")
    # @select(
    #     custom_id="categories",
    #     row=2,
    #     placeholder="Categories",
    #     min_values=1,
    #     max_values=6,
    #     options=[
    #         SelectOption(label="Waifu"),
    #         SelectOption(label="Husbando"),
    #         SelectOption(label="Neko", default=self.categories.contains(ImageCategory.NEKO)),
    #         SelectOption(label="Catboy", default=self.categories.contains(ImageCategory.CATBOY)),
    #         SelectOption(label="Demon Slayer", default=self.categories.contains(ImageCategory.DEMON_SLAYER)),
    #         SelectOption(label="Leng Asian Boys", default=self.categories.contains(ImageCategory.LENG_ASIAN_BOYS)),
    #     ])
    # async def category_sel(self, interaction: Interaction, select: Select):
    #     pass

class SmashOrPassInitView(View):
    def __init__(self, config: Config, serverid: int):
        self.logger = logging.getLogger("SmashOrPassInitView")
        self.config = config
        self.serverid = serverid
        super().__init__(timeout=None)

    async def __build_main_view(self, interaction: Interaction, categories: list[ImageCategory]):
        init_cat = categories[randint(0, len(categories)-1)]
        init_img = await init_cat.call(self.config, self.serverid)
        self.logger.info(f"inital image: {init_img}")
        self.logger.info(f"categories: {categories}")
        e = Embed(color=0xEE2222, title="Smash or Pass") \
            .set_image(url=init_img.url) \
            .set_footer(text=init_img.get_footer())
        e.image.url = init_img.url
        v = SmashOrPassView([init_img], categories, self.config, self.serverid)
        # v = SmashOrPassView([pull_neko(anime_apis.nekos_best.ImageCategory.CUDDLE)], [ImageCategory.WAIFU])
        # await interaction.response.edit_message(embed=e, view=v)
        self.logger.info(f"sending message edit request")
        self.logger.info(f"embed: {e}")
        self.logger.info(f"view: {v}")
        self.logger.info(f"url: {e.image.url} should be: {init_img.url}")
        self.logger.info(f"image: {e.image}")
        await interaction.response.edit_message(embed=e, view=v)

    @select(
        custom_id="category",
        placeholder="Select categories",
        min_values=1,
        max_values=len(ImageCategory._member_names_),
        options=[
            SelectOption(label="Waifu"),
            SelectOption(label="Husbando"),
            SelectOption(label="Neko"),
            SelectOption(label="Kitsune"),
            SelectOption(label="Loli"),
            SelectOption(label="jokes"),
            # SelectOption(label="Catboy"),
            # SelectOption(label="Demon Slayer"),
            # SelectOption(label="Leng Asian Boys"),
        ])
    async def category_sel(self, interaction: Interaction, select: Select):
        selected = select.values
        # hacky way to do this but idc it works
        categories: list[ImageCategory] = []
        for sel in selected:
            categories.append(ImageCategory[sel.upper().replace(" ", "_").replace("-", "_")])
        await self.__build_main_view(interaction, categories)
        self.logger.info(f"categories selected: {categories}")
        init_category = categories[randint(0, len(categories)-1)]
        self.logger.info(f"inital category: {init_category.value}")
        self.logger.info(f"inital image: {await init_category.call(self.config, self.serverid)}")

        

    # @button(
    #     custom_id="random",
    #     label="Random")
    # async def random_btn(self, interaction: Interaction, button: Button):
    #     categories: list[ImageCategory] = []
    #     for cat in ImageCategory._member_names_:
    #         categories.append(ImageCategory[cat])
    #     await self.__build_main_view(interaction, categories)

    @button(
        custom_id="all",
        label="All")
    async def all_btn(self, interaction: Interaction, _):
        categories: list[ImageCategory] = []
        for cat in ImageCategory._member_names_:
            categories.append(ImageCategory[cat])
        await self.__build_main_view(interaction, categories)
