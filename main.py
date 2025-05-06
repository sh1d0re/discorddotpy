import os
os.system("clear")

import json
import re
from datetime import datetime
import random
import time
import platform
import base64
from utils import removeAnsiEscapeCodes, applyTextPadding, log, raiseError

random.seed(time.time() * random.randint(100, 999))

try:
    import discord
except ModuleNotFoundError:
    if input("Discord.py not found. Install? [y/n]").lower() == "y":
        os.system("pip install discord")

bot = discord.Client(intents = discord.Intents.all())

config = json.load(open('config.json'))

helpDiscordEmbed = discord.Embed(title="Bot Information",
    description="",
    color=0x00ff00
)
for trigger in config["triggers"]["message-triggers"].keys():
    helpDiscordEmbed.add_field(
        name=f"""`{config["triggers"]["message-triggers"][trigger]["trigger-message"]}` (*{config["triggers"]["message-triggers"][trigger]["trigger-operator"]}*) - **{trigger}**""",
        value=f"""{config["triggers"]["message-triggers"][trigger]["description"]}""",
        inline=False
    )

def replaceVariables(text:str, passedVariables={}):
    variables = {
        "DATETIME": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "CREDITS": "Created by Sh1d0re. Coded in Python (discord.py). Licensed in GPL-3.0",
    } | passedVariables | config["variables"]
    randomFunctionPattern = r'RANDOM\((\d+), (\d+)\)'
    randomFunctionPattern = re.findall(randomFunctionPattern, text)
    if randomFunctionPattern:
        startFrom, endWith = randomFunctionPattern[0]
        text = text.replace(f"$RANDOM({startFrom}, {endWith})$", str(random.randint(startFrom, endWith)))

    for variable in variables.keys():
        text = text.replace(f"${variable}$", str(variables[variable]))

    if text == "$HELP$":
        text = helpDiscordEmbed

    return(text)

def parseVariables(commandTemplate, enteredCommand):
    placeholder_pattern = re.compile(r"\$(\d+)\$")
    regex_pattern = placeholder_pattern.sub(r"(.+?)", commandTemplate)
    full_pattern = f"^{regex_pattern}$"
    match = re.match(full_pattern, enteredCommand)
    if not match:
        return(None)
    return(list(match.groups()))

def checkInternetConnection():
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    return(os.system(f"ping {param} 8.8.8.8 &> /dev/null") == 512)

@bot.event
async def on_ready():
    guild_count = len(bot.guilds)
    botGuilds = bot.guilds
    for guild in range(len(botGuilds)):
        log(f"{botGuilds[guild].id} (Name: {botGuilds[guild].name})")
    log("Bot is in " + str(guild_count) + " servers.")
    statusName = config["information"]["status-name"]["status-name"]
    statusType = config["information"]["status-name"]["status-type"]
    if statusType == "playing":
        statusActivity = discord.Game(name=statusName)
    elif statusType == "streaming":
        statusActivity = discord.Streaming(name=statusName)
    elif statusType == "listening":
        statusActivity = discord.Music(
            name=statusName["name"],
            title=statusType["title"],
            artist=statusType["artist"],
            artists=statusType["artists"],
            album=statusType["album"],
            album_cover_url=statusType["album_cover_url"],
            track_id=statusType["track_url"],
            duration=statusType["duration"],
            party_id=statusType["party_id"]
        )
    await bot.change_presence(activity=statusActivity)

@bot.event
async def on_message(message):
    messageLatency = round(bot.latency * 1000)
    log(f"({messageLatency}ms) {message.guild.name} / {message.channel.name} / {message.author}  [ {message.content} ]", "msg")
    for messageTriggers in config["triggers"]["message-triggers"].keys():
        trigger = config["triggers"]["message-triggers"][messageTriggers]
        operators = [
            trigger["trigger-operator"] == "is" and trigger["trigger-message"] == message.content,
            trigger["trigger-operator"] == "in" and trigger["trigger-message"] in message.content
        ]
        if any(operators):
            for act in trigger["actions"]:
                replyWith = replaceVariables(act[1], {
                    "LATENCY": messageLatency,
                    "AUTHOR": message.author,
                    "CHANNEL": message.channel.name,
                    "CONTENT": message.content,
                    "SERVER": message.guild.name
                })
                if act[0] == "REPLY/CHANNEL":
                    if type(replyWith) == discord.Embed:
                        await message.channel.send(embed=replyWith)
                    elif type(replyWith) == str:
                        await message.channel.send(replyWith)
                elif act[0] == "REPLY/AUTHOR":
                    if type(replyWith) == discord.Embed:
                        await message.author.send(embed=replyWith)
                    elif type(replyWith) == str:
                        await message.author.send(replyWith)

                elif act[0] == "PURGE":
                    await message.channel.purge(limit=int(act[1])+1)
                elif act[0] == "PYTHON":
                    try:
                        exec(base64.b64decode(act[1], "utf-8"))
                    except Exception as e:
                        log(str(e), "python")

token = str(open("token.txt").read())
log(token, "token")
if token == "":
    raiseError("Token not found in config.json (information/token)", 3, True)
if checkInternetConnection():
    raiseError("No internet connection. Try connecting to Wi-Fi when running.", 3, True)

try:
    bot.run(token)
except KeyboardInterrupt:
    raiseError("Session inturrupted by user", "error", 1, True)
except Exception as e:
    raiseError(str(e), "error", 2)
