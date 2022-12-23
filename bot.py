# bot.py

# load discord
import os
import discord
import math
import json
from discord import app_commands
from dotenv import load_dotenv
from tabulate import tabulate
from datetime import datetime as dt
from datetime import timedelta
from datetime import date
import random
import asyncio
from decimal import Decimal

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# user data

data = json.load(open("data.json", "r"))
ddms = {}

# predefined client/embed

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        for guild in self.guilds:
            self.tree.clear_commands(guild=guild)
        #self.tree.add_command(self.tree.get_command("challenges"), override=True)
        for x in ddms:
            ddms[x] = {"gen": {"msg": [], "opt": []}, "challs": {"msg": [], "opt": []}}
        data = imdata()
        for user in data:
            for generator in ["como", "S"]:
                for n in [9, 10]:
                    data[user][generator][f"gen{n}"] = {"total": 0, "bought": 0}
        exdata(data)
        await self.tree.sync()

class error_embed(discord.Embed):
    def __init__(self, error):
        super().__init__()
        if error == "ongoing simulation":
            self.title = f"error! {error}"
            self.description = "you already have an ongoing simulation. please wait for the simulation to finish first."
        else:
            self.title = f"error! invalid {error}."
            self.description = f"check `/help` to see if your {error.split()[-1]} is in the right format. otherwise, please join the support server here.\nhttps://discord.gg/GPfpUNmxPP"
        self.color = discord.Color.dark_red()

# views

class GDropdown(discord.ui.Select):
    def __init__(self, iuid):
        self.iuid = iuid
        options = [
            discord.SelectOption(label='S')
        ]
        data = imdata()
        if data[iuid]["prestige"]["ggrav"] > 0:
            options.append(discord.SelectOption(label='como'))
        super().__init__(placeholder='pick a generator type', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        global ddms
        iuid = str(interaction.user.id)
        ddms[iuid]["gen"]["opt"] = self.values[0]
        generator = ddms[iuid]["gen"]["opt"]
        data = imdata()
        dat = data[iuid]
        ogr = ddms[iuid]["gen"]["msg"][-1]
        buttons = SButtons(iuid) if generator == "S" else CButtons(iuid)
        embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s {generator} generation.SSS", description=ps(data, iuid)+f"\n```{prnt(iuid, generator)}```")
        await ogr.edit(embed=embed,view=buttons)
        if str(iuid) == str(self.iuid):
            while 1:
                dat = imdata()[iuid]
                gens = ["S"]
                if dat["prestige"]["ggrav"] > 0:
                    gens.append("como")
                if dat["prestige"]["egrav"] > 0:
                    gens.append("Σ")
                for gen in gens:
                    dat = imdata()[iuid]
                    generator = ddms[iuid]["gen"]["opt"]
                    buttons = SButtons(iuid) if generator == "S" else CButtons(iuid)
                    await asyncio.sleep(1)
                    dat = await tick(str(iuid), gen, 1000, interaction, dt.now())
                    dat = dat[iuid]
                    dat["time"] += 1 
                    dat["access"] = str(dt.now())
                    data[iuid] = dat
                    exdata(data)
                    embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s {generator} generation.SSS", description=ps(data, iuid)+f"\n```{prnt(iuid, generator)}```")
                    try:
                        await ogr.edit(embed=embed,view=buttons)
                    except:
                        await interaction.followup.send(embed=embed,view=buttons)
        else:
            await interaction.followup.send(embed=discord.Embed(title="not your game!", description="please run the command yourself.", color=discord.Color.dark_red()), ephemeral=True)

class GDView(discord.ui.View):
    def __init__(self, iuid):
        super().__init__()
        self.iuid = iuid

        # Adds the dropdown to our view object.
        self.add_item(GDropdown(iuid))

class SButtons(discord.ui.View):
    def __init__(self, iuid, timeout=180):
        super().__init__(timeout=timeout)
        self.iuid = iuid
        self.add_item(GDropdown(iuid))

    async def click(self, x, int):
        data = imdata()
        game = data[str(int.user.id)]
        price = (Decimal(2**(x))**Decimal(game["S"][f"gen{x}"]["bought"]+x))**Decimal(1 if not (game["inchallenge"]["ggrav"] == 5 and x == 1) else 2)
        if str(int.user.id) == str(self.iuid):
            if game["S"]["amount"] >= price:
                game["S"]["amount"]-= price
                game["S"][f"gen{x}"]["total"] += 1
                game["S"][f"gen{x}"]["bought"] += 1
                data[str(int.user.id)] = game
                if game["inchallenge"]["ggrav"] == 3:
                    for x in range(x-1, 0, -1):
                        game["S"][f"gen{x}"] = {"total": 0, "bought": 0}
                exdata(data)
                pr = prnt(int.user.id, "S")
                embed = discord.Embed(title=f"{int.user.display_name} ({int.user.name})'s generation.SSS", description=ps(data, str(int.user.id))+f"\n```{pr}```")
                await int.edit_original_response(embed=embed,view=SButtons(self.iuid))
            elif game["inchallenge"]["ggrav"] == 4 and x in [7, 8]:
                await int.followup.send(embed=discord.Embed(title="not available!", description="generators for S7 and S8 are not available in gdgc4.", color=discord.Color.dark_red()), ephemeral=True)
            else:
                await int.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first.", color=discord.Color.dark_red()), ephemeral=True)
        else:
            await int.followup.send(embed=discord.Embed(title="not your game!", description="please run the command yourself.", color=discord.Color.dark_red()), ephemeral=True)

    @discord.ui.button(label="S1",style=discord.ButtonStyle.gray)
    async def s1b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 1
        await self.click(x, interaction)
        
    @discord.ui.button(label="S2",style=discord.ButtonStyle.gray)
    async def s2b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 2
        await self.click(x, interaction)

    @discord.ui.button(label="S3",style=discord.ButtonStyle.gray)
    async def s3b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 3
        await self.click(x, interaction)

    @discord.ui.button(label="S4",style=discord.ButtonStyle.gray)
    async def s4b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 4
        await self.click(x, interaction)
        
    @discord.ui.button(label="max all",style=discord.ButtonStyle.green)
    async def maxallb(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        iuid = str(interaction.user.id)
        data = imdata() 
        game = data[iuid]
        if str(interaction.user.id) == str(self.iuid):
            for x in range((6 if game["inchallenge"]["ggrav"] == 4 else 8), 0, -1):
                price = (Decimal(2**(x))**Decimal(game["S"][f"gen{x}"]["bought"]+x))**Decimal(2 if (game["inchallenge"]["ggrav"] == 5 and x != 1) else 1)
                while game["S"]["amount"] >= price:
                    game["S"]["amount"] -= price
                    game["S"][f"gen{x}"]["total"] += 1
                    game["S"][f"gen{x}"]["bought"] += 1
                    data[iuid] = game
                    if game["inchallenge"]["ggrav"] == 3:
                        for x in range(x-1, 0, -1):
                            game["S"][f"gen{x}"] = {"total": 0, "bought": 0}
                    price = (Decimal(2**(x))**Decimal(game["S"][f"gen{x}"]["bought"]+x))**Decimal(2 if (game["inchallenge"]["ggrav"] == 5 and x != 1) else 1)
            for x in range(10):
                exdata(await tick(str(iuid), "S", 1, interaction, dt.now()))
                await asyncio.sleep(0.001)
            pr = prnt(iuid, "S")
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s generation.SSS", description=ps(data, iuid)+f"\n```{pr}```")
            await interaction.edit_original_response(embed=embed,view=SButtons(iuid)) 
        else:
            await interaction.followup.send(embed=discord.Embed(title="not your game!", description="please run the command yourself.", color=discord.Color.dark_red()), ephemeral=True)

    @discord.ui.button(label="S5",style=discord.ButtonStyle.gray)
    async def s5b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 5
        await self.click(x, interaction)

    @discord.ui.button(label="S6",style=discord.ButtonStyle.gray)
    async def s6b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 6
        await self.click(x, interaction)

    @discord.ui.button(label="S7",style=discord.ButtonStyle.gray)
    async def s7b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 7
        await self.click(x, interaction)

    @discord.ui.button(label="S8",style=discord.ButtonStyle.gray)
    async def s8b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 8
        await self.click(x, interaction)

    @discord.ui.button(label="grand gravity",style=discord.ButtonStyle.green)
    async def ggrav(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        data = imdata() 
        game = data[str(interaction.user.id)]
        if game["S"]["amount"] >= 24**24:
            iuid = str(interaction.user.id)
            data = imdata() 
            dat = data[iuid]
            dat, objm, objn = ggrav(dat)
            pr = prnt(iuid, "S")
            data[iuid] = dat
            exdata(data)
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s generation.SSS", description=ps(data, str(interaction.user.id))+f"\n```{pr}```")
            await interaction.edit_original_response(embed=embed,view=SButtons(iuid))
            await interaction.followup.send(embed=discord.Embed(title="grand gravity!", description=f"congrats on your {ordinal(dat['prestige']['ggrav'])} grand gravity!" + (f"\nyou have 2 more como and 1 new objekt: {objm} {objn}!") if objm != "" else ""), ephemeral=True)
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first.", color=discord.Color.dark_red()), ephemeral=True)

class CButtons(discord.ui.View):
    def __init__(self, iuid, timeout=180):
        super().__init__(timeout=timeout)
        self.iuid = iuid
        self.add_item(GDropdown(iuid))

    async def click(self, x, int):
        data = imdata()
        dt = data[str(int.user.id)]
        game = dt
        if game["como"]["amount"] >= Decimal(2**(x))**Decimal(game["como"][f"gen{x}"]["bought"]+x):
            game["como"]["amount"] -= Decimal(2**(x))**Decimal(game["como"][f"gen{x}"]["bought"]+x)
            game["como"][f"gen{x}"]["total"] += 1
            game["como"][f"gen{x}"]["bought"] += 1
            data[str(int.user.id)] = game
            exdata(data)
            pr = prnt(int.user.id, "como") 
            embed = discord.Embed(title=f"{int.user.display_name} ({int.user.name})'s generation.SSS", description=ps(data, str(int.user.id))+f"\n```{pr}```", color=discord.Color.dark_red())
            await int.edit_original_response(embed=embed,view=CButtons(self.iuid))
        else:
            await int.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

    @discord.ui.button(label="como1",style=discord.ButtonStyle.gray)
    async def s1b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 1
        await self.click(x, interaction)
        
    @discord.ui.button(label="como2",style=discord.ButtonStyle.gray)
    async def s2b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 2
        await self.click(x, interaction)

    @discord.ui.button(label="como3",style=discord.ButtonStyle.gray)
    async def s3b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 3
        await self.click(x, interaction)

    @discord.ui.button(label="como4",style=discord.ButtonStyle.gray)
    async def s4b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 4
        await self.click(x, interaction)
        
    @discord.ui.button(label="max all",style=discord.ButtonStyle.green)
    async def maxallb(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        iuid = str(interaction.user.id)
        data = imdata() 
        dt = data[iuid]
        game = dt
        for x in range(8, 0, -1):
            price = Decimal(2**(x))**Decimal(game["como"][f"gen{x}"]["bought"]+x)
            while game["como"]["amount"] >= price:
                game["como"]["amount"] -= price
                game["como"][f"gen{x}"]["total"] += 1
                game["como"][f"gen{x}"]["bought"] += 1
                data[iuid] = game
                price = Decimal(2**(x))**Decimal(game["como"][f"gen{x}"]["bought"]+x)
        exdata(data)
        pr = prnt(iuid, "como")
        embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s generation.SSS", description=ps(data, iuid)+f"\n```{pr}```")
        await interaction.edit_original_response(embed=embed,view=CButtons(iuid)) 

    @discord.ui.button(label="como5",style=discord.ButtonStyle.gray)
    async def s5b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 5
        await self.click(x, interaction)

    @discord.ui.button(label="como6",style=discord.ButtonStyle.gray)
    async def s6b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 6
        await self.click(x, interaction)

    @discord.ui.button(label="como7",style=discord.ButtonStyle.gray)
    async def s7b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 7
        await self.click(x, interaction)

    @discord.ui.button(label="como8",style=discord.ButtonStyle.gray)
    async def s8b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 8
        await self.click(x, interaction)

class CDropdown(discord.ui.Select):
    def __init__(self, iuid):
        self.iuid = iuid
        options = []
        data = imdata()
        if data[iuid]["prestige"]["ggrav"] > 0:
            options.append(discord.SelectOption(label='grand gravity challenges (gdgc)'))
        super().__init__(placeholder='pick a challenge category', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        data = imdata()
        ddms[self.iuid]["challs"]["opt"] = self.values[0]
        cat = ddms[self.iuid]["challs"]["opt"]
        inchall = data[self.iuid]["inchallenge"]["ggrav"]
        match cat:
            case "grand gravity challenges (gdgc)":
                embed = discord.Embed(title="grand gravity challenges (ggvc)", description=f"each challenge boosts the production of its corresponding generator by 8.\n{'you are not in any challenges.' if inchall == 0 else f'you are in challenge {inchall}.'}\n\n**subunits:**\nacid angel from asia / aaa: S2, S5, S7, S8\n+(kr)ystal eyes / +(kr)e: S1, S3, S4, S6")
                ogr = ddms[self.iuid]["challs"]["msg"][-1]
                for x in range(8):
                    embed.add_field(name=f"ggvc{x+1}\n{challs['ggrav'][x][0]}" + ("\n(completed)" if x+1 in data[self.iuid]["challenges"]["ggrav"] else ""), value=challs["ggrav"][x][1])
                await ogr.edit(embed=embed, view=GDGCButtons(self.iuid))

class CView(discord.ui.View):
    def __init__(self, iuid):
        super().__init__()
        self.iuid = iuid

        # Adds the dropdown to our view object.
        self.add_item(CDropdown(iuid))

class GDGCButtons(discord.ui.View):
    def __init__(self, iuid, timeout=180):
        super().__init__(timeout=timeout)
        self.iuid = iuid
        self.add_item(CDropdown(iuid))

    async def click(self, x, int):
        data = imdata()
        game = data[str(int.user.id)]
        if game["prestige"]["ggrav"] > 0:
            game["inchallenge"]["ggrav"] = x
            game["S"]["amount"], game["S"]["/s"] = 2, 0
            for n in range(8):
                game["S"][f"gen{n+1}"] = {
                    "total": 0,
                    "bought": 0,
                }
            game["como"]["power"] = 0
            game["start"] = str(dt.now())
            if x == 6:
                game["challenges"]["gdgc6"] = []
                for n in range(8):
                    y = 0.24*((8/0.24)**random.random())
                    game["challenges"]["gdgc6"].append(y)
            data[str(int.user.id)] = game
            exdata(data)
            inchall = game["inchallenge"]["ggrav"]
            embed = discord.Embed(title="grand gravity challenges (ggvc)", description=f"each challenge boosts the production of its corresponding generator by 8.\n{'you are not in any challenges.' if inchall == 0 else f'you are in gdgc{inchall}.'}\n\n**subunits:**\nacid angel from asia / aaa: S2, S5, S7, S8\n+(kr)ystal eyes / +(kr)e: S1, S3, S4, S6")
            for n in range(8):
                embed.add_field(name=f"ggvc{n+1}\n{challs['ggrav'][n][0]}" + ("\n(completed)" if n+1 in game["challenges"]["ggrav"] else ""), value=challs["ggrav"][n][1])
            await int.edit_original_response(embed=embed,view=GDGCButtons(self.iuid))
        else:
            await int.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

    @discord.ui.button(label="start challenge 1",style=discord.ButtonStyle.gray, disabled=True)
    async def ggvc1(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 1
        await self.click(x, interaction)
       # constant game variables 
    @discord.ui.button(label="start challenge 2",style=discord.ButtonStyle.gray)
    async def ggvc2(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 2
        await self.click(x, interaction)

    @discord.ui.button(label="start challenge 3",style=discord.ButtonStyle.gray)
    async def ggvc3(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 3
        await self.click(x, interaction)

    @discord.ui.button(label="start challenge 4",style=discord.ButtonStyle.gray)
    async def ggvc4(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 4
        await self.click(x, interaction)

    @discord.ui.button(label="exit challenge",style=discord.ButtonStyle.red)
    async def exit(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 0
        await self.click(x, interaction)
        
    @discord.ui.button(label="start challenge 5",style=discord.ButtonStyle.gray)
    async def ggvc5(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 5
        await self.click(x, interaction)

    @discord.ui.button(label="start challenge 6",style=discord.ButtonStyle.gray)
    async def ggvc6(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 6
        await self.click(x, interaction)

    @discord.ui.button(label="start challenge 7",style=discord.ButtonStyle.gray)
    async def ggvc7(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 7
        await self.click(x, interaction)

    @discord.ui.button(label="start challenge 8",style=discord.ButtonStyle.gray)
    async def ggvc8(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 8
        await self.click(x, interaction)

bot = MyClient(intents=intents)

topg = os.getenv('TOPGG_TOKEN')

# constant game variables

data = {}
tS = ["seoyeon", "hyerin", "jiwoo", "chaeyeon", "yooyeon", "soomin", "nakyoung", "yubin"]
tC = [f"como{x}" for x in range(8)]

challs = {
    "ggrav": [
        ["first grand gravity", "reach 24^24 for the first time."],
        ["generation (smol ver.)", "S1 generator is heavily weakened but gets an exponentially increasing bonus."],
        ["termination", "buying a generator automatically erases all lower tier generators."],
        ["triplequarterS", "S7 and S8 generators are unavailable."],
        ["it's gold? or white?", "all generator costs are squared."],
        ["dimension shift", "all generators get a random multiplier from x0.24 to 8."],
        ["two-system generation", "each generator produces the generator two tiers below. if not available, produces S."],
        ["two-system generation\n(DIMENSION ver.)", "each generator produces the nearest lower-tier generator in the same subunit. if not available, produces S."]
    ]
}

hlink = r"||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||"

story = {
    """
you wake up in an empty room. there is no one else in the room, just you...and a big screen with words on it.

slowly, you get up and approach the screen as it flickers to life.

> yoon seoyeon, you have chosen to become the first big S, or S1. out of many small s in the world, you are the first girl we discovered with the special ability to make S, a special kind of energy with supernatural properties.
> 
> you have been equipped with 2 S. these 2 S are very valuable and rare, but they will no longer be rare when we start mass producing them.
> 
> your job now is to generate as much S as possible. click the "S1" button to spend 2 S to buy your first generator.

and with that, you start your "adventure" as yoon seoyeon, stuck in a small room producing S until you can get the fuck out.
    """: "no requirement",
    """
apprehensively, you press the button. suddenly, a machine appears in front of you.

> each S1 generator allows you to produce 0.001 S per millisecond. this number may increase over time, but what's important now is that you get as many generators as possible to produce S.
> 
> when you have 4 S, you will be able to introduce another big S into the room. the second big S (S2) will not generate S, but is equipped with a generator that generates your generators.
> 
> each subsequent big S generates generators of the previous big S. for example, S3 generators will generate S2 generators, which in turn generate S1 generators, which generate S. this allows your S production to increase exponentially.
> 
> additionally, for every S you buy, you increase the production by 1/24 (exponentially).
> 
> you must unlock each S in order. for example, S3 cannot be bought unless you have at least one S2 generator.
> 
> keep generating stars until you are able to unlock more members.
    """: "buy 1 S1 generator",
    """
you press the "S2" button. suddenly, another girl appears next to you. the screen then lights up again.

> jeong hyerin, you have been chosen to become the second big S, or S2. out of many small s in the world, you are the second girl we discovered with the special ability to make S.
> 
> your job now is to generate as many S1 generators as possible. with yoon seoyeon, or S1, you will soon unlock 6 other S.
> 
> i will see you then.

"b-but," you stutter, "who are you? and why are we here? how did you find us?"

> my name is SUAH. we at MODHAUS searched far and wide through years and years of extensive research to find the 24 special girls who have the special ability.
> 
> your purpose will soon be made clear.

and with that, the screen goes blank again.
    """: "buy 1 S2 generator",
    f"""
after a few minutes of grinding, you finally have enough S to introduce S8 into the room, which the 7 of you have affectionately nicknamed the HAUS, despite it being a "room" and not a "house". 

at this point, five other members have been revealed. 
S3 lee jiwoo,
S4 kim chaeyeon,
S5 kim yooyeon,
S6 kim soomin,
and S7 kim nakyoung.

the 7 of you have been hard at work, and have produced S in a rather short amount of time.

"here goes nothing!" you quickly press the "S8" button, and the eighth girl walks in.

"hi...uh..." S8 walks in and waves shyly. "my name's gong yubin. do you guys know why we're here?"

"don't worry too much about that yet. SUAH will be here any minute..." hyerin mutters.

"SUAH? who's SUAH?" jiwoo asks.

"you'll see." you sit the last girl down in front of the screen as it lights up once again.

> greetings, seoyeon and hyerin. i see you have gathered the next 6 girls. good job.
> 
> to the other 6 of you, welcome. my name is SUAH, and i am an AI representative of MODHAUS, the secret organisation that has brought you all here.
> 
> as i told seoyeon and hyerin earlier, we at MODHAUS searched far and wide through years and years of extensive research to find the 24 special girls who have the special ability to produce S.
> 
> at the moment, we have only found the 8 of you, although many more are on the way.
> 
> right now, your task is to get to 1.333e33 S. such huge amounts of S are at the very limit of our capacity, so the S will combust and cause what is called a grand gravity, your first prestige layer. 
> 
> i will see you then.

"'prestige layer'...? this sounds like an idle game," hyerin remarked.

"that's because it is, you idiot." nakyoung deadpanned.

"is no one going to talk about how SUAH said that the S will combust?" soomin's face was filled with worry.

"we need to get out of here ASAP!" chaeyeon darted a few hurried glances around the room, looking for an exit.

"do any of you have matches? we might be able to burn the place down." jiwoo shouted.

"I HAVE A BOX!" yooyeon tossed her box of matches over, but yubin swiftly caught it.

"YOU'RE JUST GOING TO MAKE THE S COMBUST EVEN MORE! AND WE PROBABLY WON'T BE ABLE TO GET OUT OF HERE ANYWAY!" she screamed in jiwoo and yooyeon's faces.

"ooh, new girl's got an temper..." nakyoung subtly placed her hand over her mouth.

"ALRIGHT EVERYONE!" seoyeon clapped her hands to gather everyone's attention, exasperated. "we need to stay here and finish all of this so we can get out. we're going to have to trust SUAH and MODHAUS on this one. now everyone get back to work!"
    """: "buy 1 S8 generator",
    """
the smoke clears. the 8 of you emerge coughing, while the screen lights up again.

> congratulations on your first grand gravity. you have now unlocked multiple different things to boost your S production.

chaeyeon grimaced. "there's more...?"

> yes. after all, we still do not have all 24 girls yet.
> 
> anyway, back to the new things you've unlocked with the first grand gravity.
> 
> first thing you've unlocked is como. como will be used for another set of generators, and como progression will be much slower. these como generators will generate como power, which will boost your S production. you will also get (como power)^(1/24) como per second.
> 
> the second thing you've unlocked are objekts. the first 8 objekts unlock autobuyers for each of your generators so that your work will be less manual. the other 64 autobuyers boost the speed of the respective S's autobuyer.
> 
> the third thing you've unlocked is grand gravity challenges. finishing the first grand gravity was actually your first challenge, and you have completed it! the other 7 challenges boost your production, and to complete these, you will have to generate enough como for a grand gravity under harsh conditions. rewards for challenges also consist of one objekt and one como, of course.
> 
> your new task is to get all 72 objekts and finish all 8 challenges. i will see you again then. but before i leave...

a drawer popped out of the wall.

> here is two como and one objekt. with every grand gravity, you will be given one set of these, but your como doubles every grand gravity.

the objekt was a very smooth laminated piece of paper, and felt like a trading card but slightly thicker. the como, meanwhile, were shiny purple tokens.

"interesting..." seoyeon mused. "so we need to do another...71 grand gravities before suah meets us again! EVERYBODY BACK TO WORK!"
    """: "do 1 grand gravity",
    """
you finally have 72 objekts. the big screen lights up again, and everyone turns to the bright light emitting from it.

> *sighs* unfortunately, we have hit a wall.

"what?" yubin asked, "what do you mean, *a wall*?"

> unfortunately, the ruler of this universe has not allowed us to proceed. this is the end of the road for now.
> 
> they will soon make updates to this world, but for now, all you can do is keep grinding for como.
> 
> however, the owner has granted you a grand gravity autobuyer that you have unlocked at 72 objekts.

"i dont like this guy," soomin pouted.

"shush," jiwoo shushed soomin, "they might delete you."

> regardless of your opinions, i will see you soon.

and with that, the screen went blank for what would be a much longer time.

*thank you for playing the beta version of generation.SSS.*
    """: "do 72 grand gravities and finish all 8 gdgcs"
}

defdic = {
    "S": {
        "amount": 2,
        "/s": 0 
    },
    "como": {
        "amount": 0,
        "power": 1,
        "/s": 0
    },
    "tickspeed": 1,
    "start": str(dt.now()),
    "access": str(dt.now()),
    "time": 0,
    "objekts": {},
    "prestige": {
        "ggrav": 0
    },
    "challenges": {
        "ggrav": [],
        "gdgc6": []
    },
    "inchallenge": {
        "ggrav": 0
    },
    "autobuyers": {},
    "story": 0
}

for generator in defdic:
    if generator in ["S", "como", "Σ"]:
        for x in range(10):
            defdic[generator][f"gen{x+1}"] = {
                "total": 0,
                "bought": 0,
            }
for x in range(10):
    defdic["objekts"][f"S{x+1}"] = []

def lastdim(iuid, generator):
    data = imdata()
    data = data[str(iuid)][generator]
    for x in range(8, 0, -1):
        if data[f"gen{x}"]["bought"] != 0:
             return x-1
    return 0

def autoformat(num, dec=False):
    try:
        num = float(num)
    except:
        num = int(num)

    try:
        if dec:
            num = round(num, 3)
        else:
            num = math.floor(int(num) * 1000)/1000
            num = int(num) if num % 1 == 0 else num
    except:
        pass
    val = num
    num = str(num)
    if val >= 1000000:
        if "e+" not in num:
            e = len(num.split(".")[0])-1
            num = f"{num[0]}.{num[1:4]}e+{e}"
        else:
            num = f"{num[0]}.{num[2:5]}e+{num.split('e+')[1]}"
    while len(num.split(".")[-1]) < 3 and "." in num:
        num += "0"
    return num
    
def prnt(iuid, generator):
    data = imdata()
    dat = data[str(iuid)]
    if not (dat["S"]["amount"] >= 24**24 and generator == "S"):
        table = []
        for x in range(8):
            if (x <= lastdim(iuid, generator)+1) and not (dat["inchallenge"]["ggrav"] == 4 and x in [6, 7]) and not (dat[generator][f"gen1"]["total"] == 0 and x == 1):
                memb = f"S{x+1}"
                try:
                    next = max(dt.fromisoformat(dat["autobuyers"][memb]) + timedelta(seconds=2**(9-len(dat["objekts"][memb]))), dt.now())
                    wait = next - dt.now()
                    atbitv = str(min(wait.seconds, 2**(9-len(dat["objekts"][memb])))) + "s"
                except:
                    atbitv = "none"
                table.append([f"{generator}{x+1}", f"{tS[x]}", autoformat(dat[generator][f"gen{x+1}"]["total"]) + " (" + autoformat(dat[generator][f"gen{x+1}"]["bought"], dec=False) + ")", autoformat((Decimal(2**(x+1))**Decimal(dat[generator][f"gen{x+1}"]["bought"]+x+1))**Decimal(2 if (dat["inchallenge"]["ggrav"] == 5 and x != 0) else 1))] + ([atbitv] if generator == "S" else []))
        amount = autoformat(dat[generator]["amount"]) 
        ps = autoformat(dat[generator]["/s"])
        if dat["inchallenge"]["ggrav"] == 0:
            challenge = "you are not in any challenge.\n\n"
        else:
            inggravc = dat["inchallenge"]["ggrav"]
            challenge = f"you are in challenge {inggravc}.\n\n"
        pgenerator = generator if generator != "como" else "como power"
        comoa = autoformat(dat["como"]["power"])
        if generator == "como":
            amounts = f"you have {comoa} {pgenerator}. ({ps} {pgenerator}/s)\n" + (f"you have {amount} como.\n")
        else:
            amounts = f"you have {amount} {pgenerator}. ({ps} {pgenerator}/s)\n"
        return amounts + challenge + tabulate(table, headers=["gen", "member", "amount", f"cost ({generator})"] + (["autobuy"] if generator == "S" else []))
    else:
        return f"your S has combusted and caused a grand gravity. press the 'grand gravity' button to continue."

async def milli(game, generator, iuid, ticks, interaction, start):
    data = imdata() 
    game = data[iuid]
    ticks = min(ticks, 1000000)
    gen8b = game["S"]["gen8"]["bought"]
    boosts = 1
    if generator == "S":
        boosts *= Decimal(8**(lastdim(iuid, generator)))*(Decimal(24)**Decimal(gen8b))*(Decimal(game["como"]["power"])**Decimal(1/8))
    tnews = Decimal(0)
    start = dt.now()
    for n in range(ticks):
        game = imdata()[iuid]
        for x in range(8 if game["story"] < 5 else 10):
            if int(game["inchallenge"]["ggrav"]) == 7 and generator == "S" and x < 8:
                if x in [0, 1]:
                    news = Decimal(((game[generator][f"gen{x+1}"]["total"])*(boosts)*Decimal('0.001'))*(Decimal(25/24)**(game[generator][f"gen{x+1}"]["bought"])) if game["inchallenge"]["ggrav"] != 2 else (game[generator][f"gen1"]["total"])**Decimal(Decimal('0.01')*(game["time"])**Decimal('1.0038065'))*Decimal('0.001'))
                    if game["inchallenge"]["ggrav"] == 6:
                        news *= game["challenges"]["gdgc6"][x]
                    game[generator]["/s"] = news*2
                    tnews += news
                else:
                    game[generator][f"gen{x-1}"]["total"] += (game[generator][f"gen{x+1}"]["total"]*Decimal('0.001')*Decimal((game["challenges"]["gdgc6"][x]) if (game["inchallenge"]["ggrav"]) == 6 else 1)*(Decimal(25/24)**(game[generator][f"gen{x+1}"]["bought"])))
            elif int(game["inchallenge"]["ggrav"]) == 8 and generator == "S" and x < 8:
                aaa = [2, 5, 7, 8]
                kre = [1, 3, 4, 6]
                if x+1 in [s[0] for s in [aaa, kre]]:
                    news = Decimal((Decimal(game[generator][f"gen{x+1}"]["total"])*Decimal(boosts)*Decimal('0.001'))*(Decimal(25/24)**Decimal(game[generator][f"gen{x+1}"]["bought"])) if game["inchallenge"]["ggrav"] != 2 else Decimal(game[generator][f"gen1"]["total"])**Decimal(Decimal('0.01')*Decimal(game["time"])**Decimal('1.0038065'))*Decimal('0.001'))
                    if game["inchallenge"]["ggrav"] == 6:
                        news *= game["challenges"]["gdgc6"][x]
                    game[generator]["/s"] = news
                    tnews += news
                else:
                    subu = []
                    for s in aaa, kre:
                        if x+1 in s:
                            subu = s
                            break
                    game[generator][f"gen{subu[subu.index(x+1)-1]}"]["total"] += Decimal(game[generator][f"gen{x+1}"]["total"]*Decimal('0.001')*(game["challenges"]["gdgc6"][x] if game["inchallenge"]["ggrav"] == 6 else 1)*(Decimal(25/24)**Decimal(game[generator][f"gen{x+1}"]["bought"])))
            else:
                if x == 0:
                    if generator == "S":
                        news = max(Decimal(game[generator][f"gen1"]["total"])*Decimal(boosts)*Decimal('0.001') if game["inchallenge"]["ggrav"] != 2 else Decimal(game[generator][f"gen1"]["total"])**Decimal(Decimal('0.01')*Decimal(game["time"])**Decimal('1.0038065'))*Decimal('0.001')*Decimal(25/24)**Decimal(game[generator][f"gen{x+1}"]["bought"]), Decimal('0.001'))
                        if game["inchallenge"]["ggrav"] == 6:
                            news *= game["challenges"]["gdgc6"][x]
                        game[generator]["/s"] = news
                        tnews += news
                    elif generator == "como":
                        tnews += game["como"]["gen1"]["total"]*(Decimal(25/24)**Decimal(game[generator][f"gen{x+1}"]["bought"]))
                else:
                    if game["inchallenge"]["ggrav"] == 4 and x in [6, 7] and generator == "S":
                        game[generator][f"gen{x+1}"] = {"total": 0, "bought": 0}
                    else:
                        new = game[generator][f"gen{x+1}"]["total"]*(game["challenges"]["gdgc6"][x] if game["inchallenge"]["ggrav"] == 6 else 1)*(Decimal(25/24)**Decimal(game[generator][f"gen{x+1}"]["bought"]))
                        game[generator][f"gen{x}"]["total"] += Decimal(new)*Decimal('0.001')
        for x in range(8 if game["story"] < 5 else 10):
            memb = f"S{x+1}"
            try:
                later = (dt.fromisoformat(game["autobuyers"][memb]) + timedelta(seconds=2**(9-len(game["objekts"][memb]))))
                if generator + str(x+1) in game["autobuyers"] and start + timedelta(microseconds=1000*n) >= later:
                    while 1:
                        price = (Decimal(2**(x+1))**Decimal(game[generator][f"gen{x+1}"]["bought"]+x+1))**Decimal(2 if (game["inchallenge"]["ggrav"] == 5 and x != 0) else 1)
                        game["autobuyers"][memb] = str(dt.now())
                        if game[generator]["amount"] >= price:
                            game[generator]["amount"] -= price
                            game[generator][f"gen{x+1}"]["total"] += 1
                            game[generator][f"gen{x+1}"]["bought"] += 1
                        else:
                            break
            except:
                pass
        try:
            atb_ggrav = game["autobuyers"]["ggrav"]
        except:
            pass
        else:
            if game["S"]["amount"] >= 24**24 and start + timedelta(microseconds=1000*n) > dt.fromisoformat(atb_ggrav) + timedelta(seconds=1):
                iuid = str(interaction.user.id)
                game, objm, objn = ggrav(game)
                data[iuid] = game
        tnews = Decimal(str(tnews))
        game[generator]["amount" if generator == "S" else "power"] += tnews
        data[iuid] = game
        exdata(data)
    return game, tnews

def imdata():
    data = json.load(open("data.json", "r"))
    exdata(data)
    for uid in data:
        game = data[uid]
        for generator in game:
            if type(game[generator]) == dict:
                for gen in game[generator]:
                    if gen[:3] == "gen":
                        for x in game[generator][gen]:
                            game[generator][gen][x] = Decimal(round(float(game[generator][gen][x]), 3))
                    else:
                        try:
                            game[generator][gen] = Decimal(round(float(game[generator][gen]), 3))
                        except:
                            pass
        data[uid] = game
    return data

def exdata(data):
    for uid in data:
        game = data[uid]
        for generator in game:
            if type(game[generator]) == dict:
                for gen in game[generator]:
                    if gen[:3] == "gen":
                        for x in game[generator][gen]:
                            game[generator][gen][x] = str(game[generator][gen][x])
        data[uid] = game
    json.dump(data, open("data.json", "w"), indent=4, default=str)

async def tick(iuid, generator, ticks, interaction, start):
    data = imdata()
    game = data[str(iuid)]
    game = await milli(game, generator, iuid, ticks, interaction, start)
    game = game[0]
    tnews = await milli(game, generator, iuid, 1000, interaction, start)
    tnews = tnews[1]
    game[generator]["/s"] = tnews
    data[iuid] = game
    exdata(data)
    return data

def ps(data, iuid):
    game = imdata()[iuid]
    st = game["story"]
    if game["S"]["gen1"]["bought"] > 0:
        st = max(st, 1)
    if game["S"]["gen2"]["bought"] > 0:
        st = max(st, 2)
    if game["S"]["gen8"]["bought"] > 0:
        st = max(st, 3)
    if game["prestige"]["ggrav"] > 0:
        st = max(st, 4)
    if game["prestige"]["ggrav"] >= 72 and sorted(game["challenges"]["ggrav"]) == [1, 2, 3, 4, 5, 6, 7, 8]:
        st = max(st, 5)
    data[iuid]["story"] = st
    exdata(data)

    return f"**chapter {st}**\n" + list(story.keys())[st] + ("" if st == len(story)-1 else f"\n*{list(story.values())[st+1]} to unlock next chapter*")

def progress(num, length):
    str = "|"
    for x in range(num):
        str += "S"
    while len(str) < length:
        str += " "
    str += "|"
    return str

def ggrav(dat):
    objm, objn = "", ""
    game = dat
    game["S"]["amount"], game["S"]["/s"] = 2, 0
    game["como"]["amount"] += int(2**(game["prestige"]["ggrav"]))
    game["como"]["power"] = 0
    for x in range(8):
        game["S"][f"gen{x+1}"] = {
            "total": 0,
            "bought": 0,
        }
    full = True
    if game["prestige"]["ggrav"] >= 72:
        game["autobuyers"]["ggrav"] = str(dt.now())
    for member in game["objekts"]:
        if len(game["objekts"][member]) != 9:
             full = False
             break
    if not full:
        if len(game["autobuyers"]) == 8:
            while 1:
                objm = "S" + str(random.choice(range(8))+1)
                if len(game["objekts"][objm]) != 9:
                    break
            while 1:
                objn = f"10{random.choice(range(8))+1}"
                if objn not in game["objekts"][objm]:
                    break
        else:
            while 1:
                objm = "S" + str(random.choice(range(8))+1)
                objn = "100"
                if objm not in game["autobuyers"]:
                    game["autobuyers"][objm] = str(dt.now())
                    break
        game["objekts"][objm].append(objn)
    if game["prestige"]["ggrav"] == 0:
        game["challenges"]["ggrav"].append(1)
    elif game["inchallenge"]["ggrav"] != 0:
        game["challenges"]["ggrav"].append(game["inchallenge"]["ggrav"])
        game["inchallenge"]["ggrav"] = 0
    game["start"] = str(dt.now())
    game["prestige"]["ggrav"] += 1
    return dat, objm, objn

def ordinal(num):
    num = str(num)
    match num[-1]:
        case "1":
            try:
                num[-2]
            except:
                return "st"
            else:
                end = "th" if num[-2] == "1" else "st"
        case "2":
            try:
                num[-2]
            except:
                return "nd"
            else:
                end = "th" if num[-2] == "1" else "nd"
        case "3":
            try:
                num[-2]
            except:
                return "rd"
            else:
                end = "th" if num[-2] == "1" else "rd"
        case _:
            end = "th"
    return str(num) + end

# commands
@bot.tree.command(name="generation", description="play")
async def generation(interaction):
    await interaction.response.defer()
    try:
        global defdic 
        data = imdata()
        iuid = str(interaction.user.id)
        try:
            data[iuid]
        except:
            defdic["start"] = str(dt.now())
            defdic["access"] = str(dt.now())
            data[iuid] = defdic 
            exdata(data)

        try:
            ddms[iuid]
        except:
            ddms[iuid] = {"gen": {"msg": [], "opt": []}, "challs": {"msg": [], "opt": []}}

        embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s generation.SSS", description=f"pick a generator type to proceed.")
        await interaction.followup.send(embed=embed, view=GDView(iuid))
        ddms[iuid]["gen"]["msg"].append(await interaction.original_response())
    except:
        pass

@bot.tree.command(name="objekts", description="view objekts")
async def objekts(interaction):
    global defdic
    data = imdata()
    iuid = str(interaction.user.id)
    try:
        data[iuid]
    except:
        defdic["start"] = str(dt.now())
        defdic["access"] = str(dt.now())
        data[iuid] = defdic 
        exdata(data)

    while 1:
        await asyncio.sleep(1)
        table = []
        data = imdata()
        for memb in data[iuid]["objekts"]:
            table.append([f"\n{memb}"])
            objekts = "" 
            data[str(interaction.user.id)]["objekts"][memb].sort()
            for obj in [f"10{x}" for x in range(0, 9)]:
                if obj in data[str(interaction.user.id)]["objekts"][memb]:
                    objekts += f"{obj} "
                else:
                    objekts += f"    "
            table[-1] += [objekts, str(2**(9-len(data[str(interaction.user.id)]["objekts"][memb])))+"s" if memb in data[str(interaction.user.id)]["autobuyers"] else "none"]
        tab = tabulate(table, headers=["gen", "objekts", "rate"])

        embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s objekts", description=f"{sum([len(data[iuid]['objekts'][x]) for x in data[iuid]['objekts']])}/72 objekts\n```{tab}```")
        try:
            await interaction.response.send_message(embed=embed)
        except:
            try:
                await interaction.edit_original_response(embed=embed)
            except:
                pass

@bot.tree.command(name="challenges", description="view challenges")
async def challenges(interaction):
    data = imdata()
    iuid = str(interaction.user.id)

    try:
        data[iuid]
    except:
        defdic["start"] = str(dt.now())
        defdic["access"] = str(dt.now())
        data[iuid] = defdic 
        exdata(data)

    try:
        ddms[iuid]
    except:
        ddms[iuid] = {"gen": {"msg": [], "opt": []}, "challs": {"msg": [], "opt": []}}
    
    if data[iuid]["prestige"]["ggrav"] > 0:
        await interaction.response.send_message(embed=discord.Embed(title="challenges", description="pick a challenge category to proceed."), view=CView(str(interaction.user.id)))
    else:
        await interaction.response.send_message(embed=discord.Embed(title="oh no!", description="you have not yet unlocked challenges. please finish one grand gravity first.", color=discord.Color.dark_red()), ephemeral=True)
    ddms[iuid]["challs"]["msg"].append(await interaction.original_response())

@bot.tree.command(name="help", description="info on the game")
async def help(interaction):
    help = {
        "basics": "basics of the game",
        "concept": "the concept of this game was based on antimatter dimensions, a game where each dimension creates the previous dimension. i wanted to make a tripleS parody so here it is! for credits, see `/credits`",
        "S generators": "most generators usually produce the generator one tier below them (S3 generators produce S2 generators, etc.) but S1 generators produce S, a special kind of energy with supernatural properties. buying a generator also multiplies the generator's overall production by 25/24.",
        "multipliers": "boosters boost S1's production in most cases (other than some challenges like gdgc6). the main boosters you will notice are 8^(number of S - 1) and 24^(number of S8 generators).",
        "grand gravity": "the first prestige layer. S is limted at 24^24, at which a grand gravity will occur. all gravity will be reset and one objekt and 2^(number of grand gravities including this one) como will be given.",
        "objekts": "objekts either unlock (100) or boost (101-108) your autobuyers. your autobuyer interval starts at 256s, before halving with every objekt (other than 100). with all objekts, your autobuyer interval should be 1s. see `/objekts` to view all your objekts.",
        "como": "como generators work like S generators, but they produce como power, not como (which is only obtainable from grand gravity). como power is used to boost S1's overall production by (como power)^0.125.",
        "challenges": "at the moment, there is only one category of challenges, grand gravity challenges (gdgcs). these challenges require you to start from the beginning and cause a grand gravity but under limited circumstances. see `/challenges` for more.",
        "miscellaneous": "anything else",
        "saves": "your data will be automatically saved. offline progress is not supported.",
        "future plans": "- second prestige layer (event gravity)\n- kaede and dahyun will be involved (not revealing how hehe)\n- 10 event gravity challenges (egrc)\n- another (currently unnamed) layer of dimensions",
        "faq": "frequently asked questions",
        "why aren't the buttons working?": "due to the messages constantly updating as well as discord's rate limits, the buttons may not work all the time as expected, but should work most of the time. if they do not, try spamming the button.",
        "how do i make my live display (only for `/generation` and `/objekts`) update faster?": "the live display windows update every 2 to 3 seconds. if they take longer, try running less windows at a time.",
        "what do i do after i reach the current endgame?": "grind. just grind.",
        "what if i have more questions?": "open a post in the beta forum. not the main bot forum, the beta forum.",
        "why is my live display not working anymore?": "discord messages stop being available for reactions, etc. after about 10 and a half minutes. try running the command again afterwards."
    }
    headers = ["basics", "grand gravity", "miscellaneous", "faq"]

    embed = discord.Embed(title="help", description="understanding the game")
    for x in help:
        embed.add_field(name=f"__{x}__" if x in headers else x, value=help[x], inline=not x in headers)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="credits", description="view inspiration")
async def credits(interaction):
    embed = discord.Embed(title="credits", description="where the ideas for this bot came from!\nnote that fe000000 was inspired by antimatter dimensions, so if i only mention antimatter dimensions and not fe000000 for certain things although both might feature it, it means the inspiration was taken from AD.")
    fields = [
        ["each dimension produces the dimension below", "antimatter dimensions (and FE000000)"],
        ["como generators", "antimatter dimensions (and FE000000)"],
        ["autobuyers", "antimatter dimensions (and FE000000)"],
        ["gdgc 2"], ["AD challenge 3"],
        ["gdgc 3"], ["AD challenge 4"],
        ["gdgc 4"], ["AD challenge 10"],
        ["gdgc 5"], ["FE000000 challenge 5"],
        ["gdgc 6"], ["AD challenge 7"],
        ["gdgc 7, 8"], ["AD challenge 12"]
    ]
    for x in fields:
        embed.add_field(name=x[0], value=x[1])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="story", description="read the story")
async def fstory(interaction):
    data = imdata()
    iuid = str(interaction.user.id)

    try:
        data[iuid]
    except:
        defdic["start"] = str(dt.now())
        defdic["access"] = str(dt.now())
        data[iuid] = defdic 
        exdata(data)

    embeds = [discord.Embed(title="story", description="all of the story that you've unlocked so far")]
    for x in range(len(story)):
        if len(embeds[-1]) + len(list(story.keys())[x]) >= 6000:          
            embeds.append(discord.Embed(title="story", description="all of the story that you've unlocked so far"))
        if x <= data[iuid]["story"]:
            if len(list(story.keys())[x]) <= 1024:
                embeds[-1].add_field(name=f"chapter {x}", value=list(story.keys())[x], inline=False)
            else:
                chap = list(story.keys())[x].strip()
                count = 1
                while len(chap) > 1024:
                    if count == 1:
                        strl = chap[:1019].split(" ")[:-1]
                        short = " ".join(strl) + "..."
                    else:
                        strl = chap[:1016].split(" ")[:-1]
                        short = ("> " if " ".join(strl).split("\n")[1][0:2] == "> " else "") + "..." + " ".join(strl) + "..."
                    if len(embeds[-1]) + len(f"chapter {x} (part {count})" + short) >= 6000:          
                        embeds.append(discord.Embed(title="story", description="all of the story that you've unlocked so far"))
                    embeds[-1].add_field(name=f"chapter {x} (part {count})", value=short, inline=False)
                    chap = chap[len(" ".join(strl)):].strip()
                    count += 1
                embeds[-1].add_field(name=f"chapter {x} (part {count})\n({list(story.values())[x]})", value=("> " if [l for l in " ".join(chap).split("\n") if l.strip() != ""][1].strip()[0] == ">" else "") + "..." + chap, inline=False)
        else:
            embeds[-1].add_field(name=f"chapter {x}", value=f"???\n{list(story.values())[x]} to unlock", inline=False)
    
    for x in embeds:
        try:
            await interaction.response.send_message(embed=x)
        except:
            await interaction.followup.send(embed=x)

@bot.tree.command(name="multipliers", description="see your multipliers or boosts")
async def multipliers(interaction):
    data = imdata()
    iuid = str(interaction.user.id)

    try:
        data[iuid]
    except:
        defdic["start"] = str(dt.now())
        defdic["access"] = str(dt.now())
        data[iuid] = defdic 
        exdata(data)
    game = data[iuid]

    embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s boosts", description="boosty woosty ehehe.")
    soverall = f"x{autoformat(8**(lastdim(iuid, 'S')))} (`8^({lastdim(iuid, 'S')}-1`), {lastdim(iuid, 'S')+1} big S)"
    if lastdim(iuid, "S") == 7:
        gen8b = game["S"]["gen8"]["bought"]
        soverall += f"\nx{autoformat(24**Decimal(gen8b))} (`24^{autoformat(gen8b)}`, S8 generators bought)"
    if game["prestige"]["ggrav"] > 0:
        soverall += f"\nx{autoformat(Decimal(game['como']['power'])**Decimal('0.125'))} (`" + autoformat(game["como"]["power"]) + f"^0.125`, como generators)"
    embed.add_field(name="overall S production (S1)", value=soverall, inline=False)
    for x in range(lastdim(iuid, "S")+1):
        count = int(game["S"][f"gen{x+1}"]["bought"])
        mult = f"\n\nx{autoformat(Decimal(25/24)**Decimal(count), dec=True)} (`(25/24)^{autoformat(count)}`, S{x+1} generators bought)"
        if x+1 in game["challenges"]["ggrav"]:
            mult += f"\nx8 (gdgc{x+1} completed)"
        if game["inchallenge"]["ggrav"] == 6:
            randm = game["challenges"]["gdgc6"][x]
            mult += f"\nx{randm} (in gdgc6)"
        embed.add_field(name=f"S{x+1}" + (" (disabled)" if x in [6, 7] and game["inchallenge"]["ggrav"] == 4 else ""), value=mult, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="viewprofile", description="view your profile.")
async def viewprof(interaction):
    data = imdata()
    iuid = str(interaction.user.id)

    try:
        data[iuid]
    except:
        defdic["start"] = str(dt.now())
        defdic["access"] = str(dt.now())
        data[iuid] = defdic 
        exdata(data)
    game = data[iuid]

    bio = game["profile"]["bio"]

    if bio == "":
        bio = "you have not picked a bio. use `/addbio` to add a bio to your account."

    image = game["profile"]["image"]

    embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s profile", description=f"{bio}") 
   
    embed.set_thumbnail(url=interaction.user.avatar)

    fields = {
        "S": f"{autoformat(game['S']['amount'])} ({autoformat(game['S']['/s'])}/s)"
    }

    fco, dco = 0, 0
    for m in game["objekts"]:
        for o in game["objekts"][m]:
            match o[0]:
                case "1":
                    fco += 1
                case "2":
                    dco += 1

    if game["prestige"]["ggrav"] > 0:
        ggravf = {
            "como": f"{autoformat(game['como']['amount'])} ({autoformat(game['como']['/s'])}/s)",
            "grand gravities": autoformat(game["prestige"]["ggrav"]),
            "first class objekts": autoformat(fco),
        }
        fields = {**fields, **ggravf}

    #if game["prestige"]["egrav"] > 0:
    if 1 == 2:
        ggravf = {
            "Σ": f"{autoformat(game['Σ']['amount'])} ({autoformat(game['Σ']['/s'])}/s)",
            "event gravities": autoformat(game["prestige"]["egrav"]),
            "second class objekts": autoformat(dco),
            "gdgcs completed": autoformat(len(game['challenges']['ggrav']))
        }
        fields = {**fields, **ggravf}

    for n, v in game["inchallenge"].items():
        match n:
            case "ggrav":
                chall = "gdgc"
            case "egrav":
                chall = "edgc"
            case _:
                chall = ""
        if v == 0:
            stat = f"you are not in any {chall}."
        else:
            stat = f"you are in {chall}{v}."
        embed.add_field(name=chall, value=stat)

    for n, v in fields.items():
        embed.add_field(name=n, value=v, inline=not n in ["S", "como", "Σ"])

    embed.set_image(url=image)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="editprofile", description="update your gif/bio in your profile.")
async def editprof(interaction, updating: str, newvalue: str):
    data = imdata()
    iuid = str(interaction.user.id)

    try:
        data[iuid]
    except:
        defdic["start"] = str(dt.now())
        defdic["access"] = str(dt.now())
        data[iuid] = defdic 
        exdata(data)
    
    
    if updating in ["bio", "image"]:
        data[iuid]["profile"][updating] = newvalue
        exdata(data)
        embed = discord.Embed(title=f"your new {updating}!", description=(f"your {updating} has been set to ```{newvalue}```" if updating == "bio" else f"your {updating} has been updated!") + "\ncheck `/viewprofile` to see how it looks!")
    else:
        embed = discord.Embed(title="invalid variable!", description="please use either 'bio' or 'image'.")

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
