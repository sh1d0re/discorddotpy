import re
import json
from datetime import datetime

config = {"server-side-settings": {"console-log-output": "True", "message-console-log-output": "True", "save-log-as-file": "False"}}

def removeAnsiEscapeCodes(s):
    return(re.sub(r'\x1b\[[^m]*m', '', s))

def applyTextPadding(text:str, maxLength:int, paddingCharacter:str, alignment:str, alignCenterTo="right", removeAnsi=False):
    textLength = len(removeAnsiEscapeCodes(text)) if removeAnsi else len(text)
    paddingTextLength = int(maxLength - (textLength))
    halfPaddingTextLength = int(maxLength - (textLength % maxLength)) / 2
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

    return(paddedText)

fullLogOutput = {}
def log(logMessage:str, type = "log"):
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logTypes = {
        "msg": "\x1b[33mMSG\x1b[0m",
        "log": "\x1b[35mLOG\x1b[0m",
        "info": "\x1b[94mINFO\x1b[0m",
        "token": "\x1b[31mTOKEN\x1b[0m    \x1b[30;40;2;3;5;9m",
        "python": "\x1b[34;1mPYTHON\x1b[0m",
        "error": "\x1b[31;1mERROR\x1b[0m"
    }
    logTypesName = logTypes.keys()

    if not(type in logTypesName):
        type = "log"

    if bool(config["server-side-settings"]["console-log-output"]):
        for logType in logTypesName:
            if type == logType:
                print(f"\x1b[0m\x1b[90m{currentTime} {applyTextPadding(logTypes[logType], 9, " ", "left", removeAnsi=True)}{logMessage}\x1b[0m")
                break
        else:
            print(f"\x1b[90m{currentTime} {logTypes["msg"]}{logMessage}\x1b[0m")
    if bool(config["server-side-settings"]["save-log-as-file"]):
        fullLogOutput["currentTime"] = [type, removeAnsiEscapeCodes(logMessage)]

def raiseError(errorMsg:str, level:int, terminateSession:bool):
    warningInitials = ["\x1b[32;1m[1]", "\x1b[33;1m[2]", "\x1b[31;1m[3]"]
    log(f"{warningInitials[level - 1]} \x1b[3m{errorMsg}\x1b[0m", "error")
    if terminateSession:
        log("Terminating session...", "error")
        print(fullLogOutput)
        if config["server-side-settings"]["save-log-as-file"]:
            saveFullLogOutput()
        exit()

def saveFullLogOutput():
    totalExecutions = json.load(open("data/.backgroundData.json"))["total-executions"]
    with open(f"logs/{int(totalExecutions)}.json") as logFile:
        json.dump(fullLogOutput, logFile)

log("Loading config.json...")
try:
    config = json.load(open('config.json'))
    log(f"Executing with the following configurations:\n\x1b[7m{config}\x1b[0m")
except FileNotFoundError:
    raiseError("config.json not found!", 3, True)