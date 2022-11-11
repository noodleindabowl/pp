#!/usr/bin/env python3
#
# Copyright (C) 2022 noodleindabowl.
#
# This file is part of craiyon_request, an automation script for
# querying www.craiyon.com.
# License: BSD-3-Clause.

"""cool discord bot!!"""
import asyncio
import logging
import random
import unicodedata
import io

import discord
from arsenic import services, browsers, get_session
from craiyon_request import craiyon_request

# webdriver options
CRAIYON_URL = "https://www.craiyon.com/"
GECKDRIVER = "./geckodriver"
WEBDRIVER_LOG = "geckodriver.log"
WEBDRIVER_LOG_MODE = "w"
WEBDRIVER_OPTIONS = {
    "moz:firefoxOptions": {
        "args": ["-headless"],
    }
}
MYSESSION = None

# logging
BOT_LOG = "bot.log"
handler = logging.FileHandler(BOT_LOG, encoding="UTF-8")
discord.utils.setup_logging(handler=handler, level=logging.DEBUG)
# client
intents = discord.Intents.default()
intents.message_content = True
activity = discord.Activity(name="!pp help",
    type=discord.ActivityType.listening)
client = discord.Client(intents=intents, activity=activity)

# bot info
BOT_NAME = "peepeepoopoo"
BOT_SHORTNAME = "pp"
BOT_PREFIX = "!pp"
# emojis
UNICODE_HEART = unicodedata.lookup("Heavy Black Heart")
UNICODE_PEANUTS = unicodedata.lookup("Peanuts")
# other
long_commands = {
    "dalle": {"in_use": False, "user": None},
}
# bot messages
BOT_GREETING = "haiiiii ^_^ hi!! hiiiiii <3 haiiiiii hii :3"
USAGE = ":heart:*USAGE*:heart: :"
WARN = ":scream_cat:*WARNING*:scream_cat: :"
YOUR_QUERY = "*your_query*"
WARN_DALLE_IN_USE = WARN + (" dalle command cannot run multiple times! please"
"wait for last request to finish! OwO")
GENERIC_ERROR_MESSAGE = ("OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A "
                         "wittle fucko boingo! The code monkeys at our "
                         "headquarters are working VEWY HAWD to fix this!")
AVAILABLE_COMMANDS = """
| **!pp help** -> show this message
| **!pp reverse <text>** -> reverse message to impress your homies
| **!pp peanut <text>** -> add nuts to message
| **!pp ask <text>** -> ask pp anything!
| **!pp dalle <text>** -> get AI-generated art of your query
| **!pp dice <number>x<sides>** -> roll some dice!
"""
COMMAND_HELP = "idk how to do that :crying_cat_face:\ntype **!pp help** to see what i can do!"


async def main():
    """start client"""
    token = get_token()
    with io.open(WEBDRIVER_LOG, WEBDRIVER_LOG_MODE, encoding="utf-8"
    ) as log_stream:
        service = services.Geckodriver(binary=GECKDRIVER, log_file=log_stream)
        browser = browsers.Firefox(**WEBDRIVER_OPTIONS)
        async with get_session(service, browser) as session:
            global MYSESSION
            MYSESSION = session
            await session.get(CRAIYON_URL);
            await client.start(token)

def get_token():
    """read bot token from file"""
    with open("token", encoding="utf-8") as file:
        return file.read().strip()


####bot events#################################################################

@client.event
async def on_connect():
    """discord connection event"""
    print("connected to discord")

@client.event
async def on_ready():
    """login event"""
    print(f"logged in as {client.user}")

@client.event
async def on_message(message):
    """message sent in server event"""
    if message.author == client.user:
        # ignore your own messages
        return
    content = message.content
    if content.startswith(BOT_PREFIX):
        # run command
        try:
            await execute_command(message)
        except Exception as e:
            await message.channel.send(
                f"{message.author.mention}! {GENERIC_ERROR_MESSAGE}")
            raise e
    elif BOT_NAME in content or BOT_SHORTNAME in content:
        # say hello
        await message.channel.send(BOT_GREETING)


####bot commands###############################################################

async def execute_command(message):
    """all bot commands defined and called here"""
    content, channel = message.content, message.channel
    message_body = content[len(BOT_PREFIX):].strip()
    if len(message_body) == 0:
        await channel.send("no commands? :pleading_face:")
        return
    command, *text = message_body.split(" ", 1)
    text = "".join(text)
    match command:
        case "help":
            await channel.send(AVAILABLE_COMMANDS)
        case "reverse":
            await reverse(text, channel)
        case "peanut":
            await peanut(text, channel)
        case "ask":
            await ask(text, channel)
        case "dalle":
            await dalle(text, channel, message.author)
        case "dice":
            await dice(text, channel)
        case _:
            await channel.send(COMMAND_HELP)

async def reverse(text, channel):
    """send back reversed text"""
    if text == "":
        await channel.send(
            f"{USAGE} {BOT_PREFIX} reverse {YOUR_QUERY}")
        return
    await channel.send(text[::-1])

async def peanut(text, channel):
    """replace random letters with the peanuts emoji"""
    text_length = len(text)
    if text_length == 0:
        await channel.send(
            f"{USAGE} {BOT_PREFIX} peanut {YOUR_QUERY}")
        return
    if text_length == 1:
        # send one peanut
        await channel.send(UNICODE_PEANUTS)
        return
    # insert <= text_length number of peanuts into string and send
    peanut_number = random.randint(1, int(text_length/2))
    textarr = list(text)
    for _ in range(peanut_number):
        i = random.randrange(0, text_length)
        textarr[i] = UNICODE_PEANUTS
    response = "".join(textarr)
    await channel.send(response)

async def ask(text, channel):
    """answer a question with yes or no, like ben"""
    if text == "":
        await channel.send(f"{USAGE} {BOT_PREFIX} ask {YOUR_QUERY}")
        return
    if random.random() >= 0.5:
        await channel.send("Yes.")
    else:
        await channel.send("No.")

async def dalle(text, channel, user):
    """fetch AI art from www.craiyon.com and post it to requester"""
    if long_commands["dalle"]["in_use"]:
        await channel.send(WARN_DALLE_IN_USE)
        return
    if text == "":
        await channel.send(f"{USAGE} {BOT_PREFIX} dalle {YOUR_QUERY}")
        return
    # remember current user
    long_commands["dalle"]["in_use"] = True
    long_commands["dalle"]["user"] = user
    # generate image
    await channel.send(f"hewwo {user.mention}! AI art of \"{text}\" is being generated just for you!")
    result = await craiyon_request.generate_image(MYSESSION, text)
    # convert pillow image to discord file and send
    with io.BytesIO() as image_bytes:
        result.save(image_bytes, "JPEG")
        image_bytes.seek(0)
        result_file = discord.File(fp=image_bytes, filename="image.jpeg")
        await channel.send(
            f"{user.mention}'s \"{text}\" AI-generated art is ready!",
            file=result_file)

async def dice(text, channel):
    num, _, sides = text.rpartition("x")
    if not num.isdigit() or not sides.isdigit():
        await channel.send(f"{USAGE} {BOT_PREFIX} dice **number**x**sides**")
        return
    num, sides = int(num), int(sides)
    # handle defective input
    if num <= 0 and sides <= 0:
        await channel.send("you ever rolled a die before? -.-")
        return
    elif num <= 0:
        mock = "zero" if num == 0 else "a negative number of"
        await channel.send(f"silly you cant roll {mock} dice -_-\"")
        return
    elif sides <= 0:
        mock = "zero" if num == 0 else "negative"
        await channel.send(f"silly you cant roll a {mock} sided dice -_-\" (somehow you can roll one and two sided dice though...)")
        return
    # roll dice
    result = sum([random.randint(1, sides) for _ in range(num)])
    await channel.send(f"rolled a {result} :game_die:")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
