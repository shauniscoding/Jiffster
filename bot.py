import discord
from discord.ext import commands
import discord
from discord.ext import commands, tasks
import random
import asyncio
import requests
import json
from dotenv import load_dotenv
import os

# environment variables
load_dotenv() 
target_channel_id = os.getenv('TARGET_CHANNEL_ID')
api_key_klipy = os.getenv('API_KEY_KLIPY')
discord_bot = os.getenv('DISCORD_BOT')

intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

# List of messages to pick from
messages = [
    "Hello everyone!",
    "How's it going?",
    "Did you know? Discord bots are cool!",
    "Stay hydrated!",
    "Here's a random fact!",
]

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}!")

saved_messages = []

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    saved_messages.append(
        {
            'content': message.content,
            'author': message.author.name,
            'timestamp': message.created_at
        }
    )
    await bot.process_commands(message)

    
# command to see saved messages
@bot.command()
async def messages(ctx):
    outputString = "Saved Messages:\n"
    recent = saved_messages[-10:] 

    for msg in recent:
        outputString += f"{msg['timestamp']} - {msg['author']}: {msg['content']}\n"

    if len(outputString) > 1900:
        outputString = outputString[:1900] + "\n... (truncated)"

    saved_messages.clear()

    await ctx.send(f"```{outputString}```") 

# command to send a random message from the list
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.name}!')

# command to get a random gif from the Klipy API
@bot.command()
async def gifMe(ctx):
    url = f"https://api.klipy.com/api/v1/{api_key_klipy}/gifs/trending"

    payload = {}
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()  # convert to Python dict
    gif = data["data"]["data"] #This is now a list 
    gifDict = random.choice(gif)
    gifUrl = gifDict["file"]["hd"]["gif"]["url"]

    await ctx.send(gifUrl)

# command to flip a coin
@bot.command()
async def flipCoin(ctx):
    result = random.choice(["Heads", "Tails"])

    if result == "Heads":
        with open("images/heads.png", "rb") as f:
            file = discord.File(f, filename="heads.png")
            await ctx.send(file=file)
    else:
        with open("images/tails.png", "rb") as f:
            file = discord.File(f, filename="tails.png")
            await ctx.send(file=file)

# command to set the mood
@bot.command()
async def setMood(ctx):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to set the mood!")
        return
    
    if not ctx.voice_client:
        vc = await ctx.author.voice.channel.connect()
    else:
        vc = ctx.voice_client

    if not vc.is_playing():
        source = discord.FFmpegPCMAudio("audio/mood1.mp4")
        vc.play(source, after=lambda e: print("✅ Done playing" if not e else f"❌ Error: {e}"))
        await ctx.send("Mood has been set 🎶")
    else:
        await ctx.send("❗ Music is already playing!")

# command to turn off mood
@bot.command()
async def stopMood(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        mood_ruined_quotes = [
            "Well, that's what she said… but now the mood is ruined.",
            "Ann, you just destroyed the entire vibe of this meeting.",
            "Whoa, whoa, whoa — can we not ruin the mood here?",
            "I regret nothing. Except maybe the mood.",
            "You've just shattered the fragile construct of our social equilibrium.",
            "Well, that's one way to kill the mood. I guess I'm just too much awesome for this party.",
            "Fact: Mood ruined. Solution: Bears. Beets. Battlestar Galactica.",
            "I drink and I know things... but you just ruined the mood.",
            "Legend—wait for it—dary mood ruined.",
            "Could this mood be any more ruined?"
        ]
        moodQuote = random.choice(mood_ruined_quotes)

        await ctx.send(moodQuote)

#command to start hopecore
@bot.command()
async def hopeCore(ctx):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to be inspired!")
        return

    if not ctx.voice_client:
        vc = await ctx.author.voice.channel.connect()
    else:
        vc = ctx.voice_client

    if not vc.is_playing():
        source = discord.FFmpegPCMAudio("audio/hope.mp4")
        vc.play(source, after=lambda e: print("✅ Done playing" if not e else f"❌ Error: {e}"))
        await ctx.send("Motivational Speech incoming...")
    else:
        await ctx.send("❗ Music is already playing!")

#Command to stop hopecore
@bot.command()
async def stopHope(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        hope_ruined_quotes = [
            "Hope is a dangerous thing for a man like me to have.",
            "There is no hope… not for me, not anymore.",
            "I hoped for too much. That was my mistake.",
            "We clung to hope… and it broke us.",
            "The last spark of hope just went out.",
            "Hope was a luxury we couldn't afford.",
            "I thought hope would save us. I was wrong.",
            "We kept hoping. And hoping. Until there was nothing left.",
            "Hope is the first step on the road to disappointment.",
            "I’ve lost hope before. But this time feels final.",
            "Even hope can’t survive in this silence.",
            "I used to believe in hope. Now I believe in reality.",
            "Hope faded, and the shadows grew longer.",
            "Sometimes, the cruelest thing you can give someone is hope.",
            "Hope didn’t die — it just stopped visiting.",
            "This place used to hold hope. Now it just echoes.",
            "Hope? Haven’t heard that name in a long time.",
            "When hope disappears, all that’s left is the waiting.",
            "Hope walked out. And it locked the door behind it.",
            "Hope whispered, but no one was listening anymore."
        ]

        hopeQuote = random.choice(hope_ruined_quotes)

        await ctx.send(hopeQuote)

# command to roll a dice
@bot.command()
async def diceRoll(ctx, count=1):
    total = 0
    try:
        count = int(count)
        if count < 1:
            await ctx.send("Please roll at least one die.")
            return
    except ValueError:
        await ctx.send("Invalid number of dice. Please enter a valid integer.")
        return
    
    for _ in range(count):
        roll = random.randint(1, 6)

        with open(f"images/dice{roll}.png", "rb") as f:
            file = discord.File(f, filename=f"dice{roll}.png")
            await ctx.send(file=file)

        total += roll

    await ctx.send(f'You rolled {total}!')





bot.run(discord_bot)
