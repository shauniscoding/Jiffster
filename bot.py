import os
import random
import requests
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import random
from openai import OpenAI


# Load environment variables
load_dotenv()
target_channel_id = int(os.getenv('TARGET_CHANNEL_ID', 0))
api_key_klipy = os.getenv('API_KEY_KLIPY')
discord_bot = os.getenv('DISCORD_BOT')
client = OpenAI()


# Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)
random_message_count = 3
counted_messages = 0


# Saved messages list (auto-trimmed)
saved_messages = []

# Random messages list
messages = [
    "Hello everyone!",
    "How's it going?",
    "Did you know? Discord bots are cool!",
    "Stay hydrated!",
    "Here's a random fact!"
]

# ============================
# BOT READY EVENT
# ============================

@bot.event
async def on_ready():
    randomGif.start()
    print(f"Bot is online as {bot.user}!")

# ============================
# COMMAND: Turn Bot on and off
# ============================
listening = True
@bot.command()
async def toggle(ctx):
    global listening
    
    if listening:
        await ctx.send(f"Turning Gifs off!")
    else:
        await ctx.send(f"Turning Gifs on!")

    listening = not listening        

# ============================
# MESSAGE LISTENER
# ============================

@bot.event
async def on_message(message):
    global counted_messages
    
    if message.author.bot:
        return

    saved_messages.append({
        'content': message.content,
        'author': message.author.name,
        'timestamp': message.created_at
    })

    counted_messages += 1

    # Limit stored messages to 200
    if len(saved_messages) > 10:
        saved_messages.pop(0)

    await bot.process_commands(message)


# ============================
# COMMAND: SEE SAVED MESSAGES
# ============================

@bot.command()
async def messages(ctx):
    output = "Saved Messages (debugging purposes):\n"
    recent = saved_messages[-10:]

    for msg in recent:
        output += f"{msg['timestamp']} - {msg['author']}: {msg['content']}\n"

    if len(output) > 1900:
        output = output[:1900] + "\n... (truncated)"

    # Clear after viewing (your original behavior)
    saved_messages.clear()

    await ctx.send(f"```{output}```")


# ============================
# COMMAND: HELLO
# ============================

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")


# ============================
# COMMAND: GIF FROM KLIPY API
# ============================

@bot.command()
async def gifMe(ctx):
    url = f"https://api.klipy.com/api/v1/{api_key_klipy}/gifs/trending"

    try:
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        data = response.json()

        if "data" not in data or "data" not in data["data"]:
            return await ctx.send("❌ Klipy API error or no GIFs found.")

        gif_list = data["data"]["data"]
        gif_dict = random.choice(gif_list)
        gif_url = gif_dict["file"]["hd"]["gif"]["url"]

        await ctx.send(gif_url)

    except Exception as e:
        await ctx.send("❌ Error accessing Klipy API.")
        print(e)


# ============================
# COMMAND: FLIP A COIN
# ============================

@bot.command()
async def flipCoin(ctx):
    result = random.choice(["Heads", "Tails"])

    filename = f"images/{result.lower()}.png"

    if not os.path.exists(filename):
        return await ctx.send("❌ Missing image files in /images folder!")

    with open(filename, "rb") as f:
        file = discord.File(f, filename=os.path.basename(filename))
        await ctx.send(file=file)


# ============================
# COMMAND: SET MOOD MUSIC
# ============================

@bot.command()
async def setMood(ctx):
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel to set the mood!")

    vc = ctx.voice_client or await ctx.author.voice.channel.connect()

    if not vc.is_playing():
        source = discord.FFmpegPCMAudio("audio/mood1.mp4")
        vc.play(source)
        await ctx.send("Mood has been set 🎶")
    else:
        await ctx.send("❗ Music is already playing!")


# ============================
# COMMAND: STOP MOOD
# ============================

@bot.command()
async def stopMood(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

        mood_ruined_quotes = [
            "Well, that's what she said… but now the mood is ruined.",
            "Ann, you just destroyed the entire vibe of this meeting.",
            "I regret nothing. Except maybe the mood.",
            "Could this mood be any more ruined?"
        ]

        await ctx.send(random.choice(mood_ruined_quotes))


# ============================
# COMMAND: HOPECORE SPEECH
# ============================

@bot.command()
async def hopeCore(ctx):
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel to be inspired!")

    vc = ctx.voice_client or await ctx.author.voice.channel.connect()

    if not vc.is_playing():
        source = discord.FFmpegPCMAudio("audio/hope.mp4")
        vc.play(source)
        await ctx.send("Motivational Speech incoming...")
    else:
        await ctx.send("❗ Music is already playing!")


# ============================
# COMMAND: STOP HOPECORE
# ============================

@bot.command()
async def stopHope(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

        hope_ruined_quotes = [
            "Hope is a dangerous thing for a man like me to have.",
            "There is no hope… not for me, not anymore.",
            "We clung to hope… and it broke us."
        ]

        await ctx.send(random.choice(hope_ruined_quotes))


# ============================
# COMMAND: DICE ROLL
# ============================

@bot.command()
async def diceRoll(ctx, count=1):
    try:
        count = int(count)
        if count < 1:
            return await ctx.send("Please roll at least one die.")
    except ValueError:
        return await ctx.send("Invalid number of dice. Please enter a valid integer.")

    total = 0

    for _ in range(count):
        roll = random.randint(1, 6)
        filename = f"images/dice{roll}.png"

        if not os.path.exists(filename):
            return await ctx.send("❌ Missing dice image files in /images folder!")

        with open(filename, "rb") as f:
            file = discord.File(f, filename=os.path.basename(filename))
            await ctx.send(file=file)

        total += roll

    await ctx.send(f"You rolled {total}!")

# ============================
# HAVE RANDOM CONTEXT INCLUDED GIFS
# ============================
@tasks.loop(seconds=10)
async def randomGif():
    global counted_messages, random_message_count, listening
    

    if counted_messages < random_message_count or not listening:
        return 
    
    counted_messages = 0
    random_message_count = random.randint(5, 15)   

    try:
        conversation_text = "\n".join(f"{m['author']}: {m['content']}" for m in saved_messages)
         
        prompt = f"""
        You are an assistant that analyzes a Discord conversation and selects a SINGLE GIF phrase
        that best represents the mood, topic, or emotional vibe of the discussion.

        Make the GIF phrase highly relevant to the conversation. 
        Consider the tone, emotions, and context of the messages — for example,
        if someone is expressing frustration about a specific topic, choose a GIF phrase that conveys that emotion and is related to that topic.

        ONLY provide the GIF phrase — do NOT include explanations, extra commentary, or formatting.

        Conversation:
        {conversation_text}
        """

        response = client.responses.create(
            model="gpt-5-nano",
            input=prompt
        )
        
        keyword_output = response.output_text
        print(keyword_output)
        saved_messages.clear()        

        url = f"https://api.klipy.com/api/v1/{api_key_klipy}/gifs/search?page=1&per_page=10&q={keyword_output}"
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        data = response.json()

        if "data" not in data or "data" not in data["data"]:
            return

        gif_list = data["data"]["data"]
        gif_dict = random.choice(gif_list)
        gif_url = gif_dict["file"]["hd"]["gif"]["url"]

        channel = bot.get_channel(target_channel_id)
        await channel.send(gif_url)


    except Exception as e:
        print(e)

# ============================
# RUN BOT
# ============================

bot.run(discord_bot)
