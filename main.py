import json
import os
import re
from datetime import datetime
import random
import time
import ast
import platform

random.seed(time.time() * random.randint(100,999))

os.system("clear")

try:
    import discord
except ModuleNotFoundError:
    if input("Discord.py not found. Install? [y/n]").lower() == "y":
        os.system("pip install discord")

config = {"server-side-settings": {"console-log-output": "True", "message-console-log-output": "True", "turn-on-logs": "False"}}
fullLogOutput = []

def applyTextPadding(text:str, maxLength:int, paddingCharacter:str, alignment:str, alignCenterTo="right"):
    paddingTextLength = int(maxLength - (len(text) % maxLength))
    halfPaddingTextLength = int(maxLength - (len(text) % maxLength)) / 2
    paddingText = "".join([paddingCharacter for _ in range(int(paddingTextLength))])
    halfPaddingText = "".join([paddingCharacter for _ in range(int(halfPaddingTextLength))])

    paddedText = ""
    if alignment == "left":
        paddedText = text + paddingText
    elif alignment == "right":
        paddedText = paddingText + text
    elif alignment == "center":
        paddedText = halfPaddingText + text + halfPaddingText
        if (paddingTextLength % 2) == 1:
            if alignCenterTo == "left":
                paddedText = paddingCharacter + paddedText
            elif alignCenterTo == "right":
                paddedText = paddedText + paddingCharacter

def log(logMessage:str, type = "log"):
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logTypes = {
        "msg": "\x1b[33m MSG\x1b[0m      ",
        "log": "\x1b[35m LOG\x1b[0m      ",
        "info": "\x1b[94m INFO\x1b[0m     ",
        "token": "\x1b[31m TOKEN\x1b[0m    \x1b[30;40;2;3;5;9m",
        "python": "\x1b[34;1m PYTHON\x1b[0m   ",
        "error": "\x1b[31;1m ERROR\x1b[0m   "
    }
    logTypesName = logTypes.keys()

    if not(type in logTypesName):
        type = "log"

    if bool(config["server-side-settings"]["console-log-output"]):
        for logType in logTypesName:
            if type == logType:
                print(f"\x1b[90m{currentTime}{logTypes[logType]}{logMessage}\x1b[0m")
                break
        else:
            print(f"\x1b[90m{currentTime}{logTypes["msg"]}{logMessage}\x1b[0m")
    if bool(config["server-side-settings"]["turn-on-logs"]):
        fullLogOutput.append([currentTime, type, logMessage])

def raiseError(errorMsg:str, level:int, terminateSession:bool):
    warningInitials = ["\x1b[32;1m[1]", "\x1b[33;1m[2]", "\x1b[31;1m[3]"]
    log(f"{warningInitials[level - 1]} \x1b[3m{errorMsg}\x1b[0m", "error")
    if terminateSession:
        log("Terminating session...", "error")
        exit()

bot = discord.Client(intents = discord.Intents.all())

log("Loading config.json...")
try:
    config = json.load(open('config.json'))
    log(f"Executing with the following configurations:\n\x1b[7m{config}\x1b[0m")
except FileNotFoundError:
    raiseError("config.json not found!", 3, True)
    exit()

def replaceVariables(text:str, passedVariables:dict):
    re.findall(r"\((\d+), (\d+)\)", )
    variables = {
        "DATETIME": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "CREDITS": "Created by Sh1d0re. Coded in Python (discord.py). Licensed in GPL-3.0",
    } | passedVariables
    randomFunctionPattern = r'RANDOM\((\d+), (\d+)\)'
    randomFunctionPattern = re.findall(randomFunctionPattern, text)
    if randomFunctionPattern:
        startFrom, endWith = randomFunctionPattern[0]
        text = text.replace(f"$RANDOM({startFrom}, {endWith})$", random.randint(startFrom, endWith))

    for variable in variables.keys():
        text = text.replace(f"${variable}$", variables[variable])
    return(text)

def checkInternetConnection():
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    return(os.system(f"ping {param} 8.8.8.8 &> /dev/null") == 512)

@bot.event
async def on_ready():
    guild_count = len(bot.guilds)
    for guild in bot.guilds:
        log(f"- {guild.id} (name: {guild.name})")
    log("Bot is in " + str(guild_count) + " servers.")
    statusName = config["information"]["status-name"]["status-name"]
    statusType = config["information"]["status-name"]["status-type"]
    if statusType == "playing":
        statusActivity = discord.Game(name=statusName)
    elif statusType == "streaming":
        statusActivity = discord.Streaming(name=statusName)
    elif statusType == "listening":
        statusActivity = discord.Music(
            name=statusName,
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
    log(f"({round(bot.latency * 1000)}ms) {message.guild.name} / {message.channel.name} / {message.author}  [ {message.content} ]", "msg")
    for messageTriggers in config["triggers"]["message-triggers"].keys():
        trigger = config["triggers"]["message-triggers"][messageTriggers]
        if trigger["trigger-operator"] == "is" and trigger["trigger-message"] == message.content:
            for act in trigger["actions"]:
                if act[0] == "REPLY/CHANNEL":
                    await message.channel.send(replaceVariables(act[1]))
                elif act[0] == "PYTHON":
                    try:
                        exec(act[1])
                    except Exception as e:
                        log(str(e), "python")

token = str(open("token.txt").read())
log(token, "token")
if token == "":
    raiseError("Token not found in config.json (information/token)", 3, True)
if checkInternetConnection():
    raiseError("No internet connection. Try connecting to Wi-Fi when running.", 3, True)
bot.run(token)