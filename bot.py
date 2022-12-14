# bot.py

# load discord
import os
import discord
import math
from discord import app_commands
from dotenv import load_dotenv
from tabulate import tabulate
from arrow import Arrow
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        for guild in self.guilds:
            self.tree.clear_commands(guild=guild)
        self.tree.add_command(self.tree.get_command("play"), override=True)
        await self.tree.sync()

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180, story=0):
        super().__init__(timeout=timeout)
        self.story = story

    @discord.ui.button(label="S1",style=discord.ButtonStyle.gray)
    async def s1b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 1
        dt = data[interaction.user.id]
        game = dt["game"]
        if game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            if game[f"s{x}gen"]["total"] == 0:
                game["time"] = 0
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
            data[interaction.user.id]["game"] = game
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
            await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)
        
    @discord.ui.button(label="S2",style=discord.ButtonStyle.gray)
    async def s2b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 2
        dt = data[interaction.user.id]
        game = dt["game"]
        if game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
            data[interaction.user.id]["game"] = game
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
            await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

    @discord.ui.button(label="S3",style=discord.ButtonStyle.gray)
    async def s3b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 3
        dt = data[interaction.user.id]
        game = dt["game"]
        if game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
            data[interaction.user.id]["game"] = game
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
            await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

    @discord.ui.button(label="S4",style=discord.ButtonStyle.gray)
    async def s4b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 4
        dt = data[interaction.user.id]
        game = dt["game"]
        if game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
            data[interaction.user.id]["game"] = game
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
            await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

    @discord.ui.button(label="max all",style=discord.ButtonStyle.green)
    async def maxallb(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        
        dt = data[interaction.user.id]
        game = dt["game"]
        for x in range(max([lastdim(game)+1, 8]), 0, -1):
            while game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
                game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
                game[f"s{x}gen"]["total"] += 1
                game[f"s{x}gen"]["bought"] += 1
                data[interaction.user.id]["game"] = game
        embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
        await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"])) 

    @discord.ui.button(label="S5",style=discord.ButtonStyle.gray)
    async def s5b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 5
        dt = data[interaction.user.id]
        game = dt["game"]
        if game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
            data[interaction.user.id]["game"] = game
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
            await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

    @discord.ui.button(label="S6",style=discord.ButtonStyle.gray)
    async def s6b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 6
        dt = data[interaction.user.id]
        game = dt["game"]
        if game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
            data[interaction.user.id]["game"] = game
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
            await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

    @discord.ui.button(label="S7",style=discord.ButtonStyle.gray)
    async def s7b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 7
        dt = data[interaction.user.id]
        game = dt["game"]
        if game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
            data[interaction.user.id]["game"] = game
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
            await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

    @discord.ui.button(label="S8",style=discord.ButtonStyle.gray)
    async def s8b(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        x = 8
        dt = data[interaction.user.id]
        game = dt["game"]
        if game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
            data[interaction.user.id]["game"] = game
            embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
            await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        else:
            await interaction.followup.send(embed=discord.Embed(title="not enough S!", description="wait till you have enough S first."), ephemeral=True)

bot = MyClient(intents=intents)

topg = os.getenv('TOPGG_TOKEN')

data = {}
tS = ["yoon seoyeon", "jeong hyerin", "lee jiwoo", "kim chaeyeon", "kim yooyeon", "kim soomin", "kim nakyoung", "gong yubin"]

story = [
    """
you wake up in an empty room. there is no one else in the room, just you...and a big screen with words on it.

slowly, you get up and approach the screen.

> yoon seoyeon, you have chosen to become the first big S, or S1. out of many small s in the world, you are the first girl we discovered with the special ability to make S.
> 
> you have been equipped with 2 S. these 2 S are very valuable and rare, but they will no longer be rare when we start mass producing them.
> 
> your job now is to generate as much S as possible. click the "S1" button to spend 2 S to buy your first generator.
    """,
    """
apprehensively, you press the button. suddenly, a machine appears in front of you.

> each S1 generator allows you to produce one S per second. this number may increase over time, but what's important now is that you get as many generators as possible to produce S.
> 
> when you have 4 S, you will be able to introduce another big S into the room. the second big S (S2) will not generate S, but is equipped with a generator that generates your generators.
> 
> each subsequent big S generates generators of the previous big S. for example, S3 generators will generate S2 generators, which in turn generate S1 generators, which generate S. this allows your S production to increase exponentially.
> 
> you must unlock each S in order. for example, S3 cannot be bought unless you have at least one S2 generator.
> 
> keep generating stars until you are able to unlock more members.
    """,
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
    """,
    """
after a few minutes of grinding, 
    """
]

def lastdim(data):
    for x in range(8):
        if data[f"s{x+1}gen"]["bought"] == 0:
             return x
    return 7

def autoformat(num):
    num = math.floor(num)
    if num >= 1000:
        return "{:.3E}".format(num).replace("E+0", "e").replace("E+", "e")
    else:
        return str(num)

def prnt(data):
    table = [["generator", "member", "number", "cost"]]
    for x in range(8):
        if x <= lastdim(data):
            table.append([f"S{x+1}", f"{tS[x]}", autoformat(data[f"s{x+1}gen"]["total"]), autoformat((2**(x+1))**(data[f"s{x+1}gen"]["bought"]+x+1))])
    S = autoformat(data["S"])
    Ss = autoformat(data["S/s"])
    minutes, seconds = divmod(data["time"], 60)
    hours, minutes = divmod(minutes, 60)
    hours, minutes, seconds = [f"0{x}" if x < 10 else str(x) for x in (hours, minutes, seconds)]
    time = f"\n\n{hours}:{minutes}:{seconds}"
    boosts = f"\n\nboosts:\n2^{lastdim(data)+1} for {lastdim(data)+1} big S"
    return f"you have {S} S. ({Ss}/s)\n" + tabulate(table) + time + boosts

def tick(data):
    data["S"] += data[f"s1gen"]["total"]*(2**(lastdim(data)+1))
    data["S/s"] = data[f"s1gen"]["total"]*(2**(lastdim(data)+1))
    for x in range(7):
        data[f"s{x+1}gen"]["total"] += data[f"s{x+2}gen"]["total"]
    game = data
    for x in range(max([lastdim(game)+1, 8]), 0, -1):
        while game["S"] >= (2**(x))**(game[f"s{x}gen"]["bought"]+x):
            game["S"] -= (2**(x))**(game[f"s{x}gen"]["bought"]+x)
            game[f"s{x}gen"]["total"] += 1
            game[f"s{x}gen"]["bought"] += 1
    data = game
    return data

def ps(data):
    st = data["story"]
    if data["game"]["s1gen"]["bought"] > 0:
        st = max([data["story"], 1])
    if data["game"]["s2gen"]["bought"] > 0:
        st = max([data["story"], 2])

    if st in [0, 1]:
        return f"**chapter {st}**\n" + story[st]
    elif st in list(range(2, 9)):
        return f"**chapter 2**\n" + story[2]
    else:
        return ""

# the command
@bot.tree.command(name="play", description="play")
async def play(interaction):
    global story

    try:
        data[interaction.user.id]
    except:
        data[interaction.user.id] = {
            "game": {
                "S": 2,
                "tickspeed": 1,
                "S/s": 0,
                "time": 0
            },
            "story": 0
        }
        for x in range(8):
            data[interaction.user.id]["game"][f"s{x+1}gen"] = {
                "total": 0,
                "bought": 0,
            }

    dt = data[interaction.user.id]
    game = dt["game"]
    embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
    await interaction.response.send_message(embed=embed,view=Buttons(story=dt["story"]))
    while 1:
        await asyncio.sleep(1)
        game = tick(game)
        dt["game"] = game
        dt["game"]["time"] += 1
        embed = discord.Embed(title=f"{interaction.user.display_name} ({interaction.user.name})'s dimenSSSions", description=ps(dt)+f"\n```{prnt(game)}```")
        await interaction.edit_original_response(embed=embed,view=Buttons(story=dt["story"]))
        S = dt["game"]["S"]
        time = dt["game"]["time"]
        if S >= 24**24:
            print(time)
        elif S >= 8**24:
            print(time, "smol")
        
bot.run(TOKEN)
