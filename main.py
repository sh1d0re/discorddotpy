import json
import os
from datetime import datetime
import time

os.system("clear")

try:
    import discord
except ModuleNotFoundError:
    if input("Discord.py not found. Install? [y/n]").lower() == "y":
        os.system("pip install discord")

def replaceVariables(text:str):
    variables = {
        "DATETIME": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "CREDITS": "Created by Sh1d0re. Coded in Python (discord.py). Licensed in GPL-3.0",
        "": ""
    }
    for variable in variables.keys():
        text = text.replace(f"${variable}$", variables[variable])
    return(text)

fullLogOutput = []
def log(logMessage:str, type = "log"):
    if type == "msg" and bool(config["server-side-settings"]["message-monitoring"]):
        print(f"\x1b[90m{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\x1b[33m MSG\x1b[0m      {logMessage}\x1b[0m")
    elif bool(config["server-side-settings"]["turn-on-logs"]):
        print(f"\x1b[90m{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\x1b[35m LOG\x1b[0m      {logMessage}\x1b[0m")

    fullLogOutput.append(logMessage)

def raiseError(errorMsg:str, level:int, terminateSession:bool):
    warningInitials = ["\x1b[32;1m[*]", "\x1b[33;1m[!]", "\x1b[31;1m[X]"]
    log(f"{warningInitials[level - 1]} - \x1b[3m{errorMsg}\x1b[0m")
    if terminateSession:
        print("Terminating session...")
        exit()

bot = discord.Client(intents = discord.Intents.all())

print("Loading config.json...")
try:
    config = json.load(open('config.json'))
    print(config)
except FileNotFoundError:
    raiseError("config.json not found! Aborting...", 3, True)
    exit()

@bot.event
async def on_ready():
    if config["server-side-settings"]["initial-guild-output"] == "True":
        guild_count = len(bot.guilds)
        for guild in bot.guilds:
            log(f"- {guild.id} (name: {guild.name})")
        log("Bot is in " + str(guild_count) + " servers.")

@bot.event
async def on_message(message):
    log(f"({round(bot.latency * 1000)}ms) {message.guild.name} / {message.channel.name} / {message.author}  [ {message.content} ]", "msg")
    await bot.change_presence(activity=discord.Game(name=''))
    for messageTriggers in config["triggers"]["message-triggers"].keys():
        trigger = config["triggers"]["message-triggers"][messageTriggers]
        if trigger["trigger-operator"] == "is":
            if trigger["trigger-message"] == message.content:
                for act in trigger["actions"]:
                    if act[0] == "REPLY/CHANNEL": await message.channel.send(replaceVariables(act[1]))


token = str(open("token.txt").read())
log(f"Running token: {token}")
if token == "":
    raiseError("Token not found in config.json (information/token)", 3, True)
else:
    bot.run(token)