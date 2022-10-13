#!/usr/bin/env python3
#
# Copyright (C) 2022 noodleindabowl.
#
# This file is part of craiyon_request, an automation script for
# querying www.craiyon.com.
# License: BSD-3-Clause.

"""cool discord bot!!"""
import logging
import random
import unicodedata

import discord

# bot info
BOT_NAME = "peepeepoopoo"
BOT_SHORTNAME = "pp"
BOT_PREFIX = "!pp"
# bot messages
BOT_GREETING = "haiiiii ^_^ hi!! hiiiiii <3 haiiiiii hii :3"
USAGE_MESSAGE = ":heart:*USAGE*:heart: :"
YOUR_MESSAGE = "*your_message*"
GENERIC_ERROR_MESSAGE = ("OOPSIE WOOPSIE!! Uwu We make a fucky wucky!! A" +
                         "wittle fucko boingo! The code monkeys at our" +
                         "headquarters are working VEWY HAWD to fix this!")
# emojis
UNICODE_HEART = unicodedata.lookup("Heavy Black Heart")
UNICODE_PEANUTS = unicodedata.lookup("Peanuts")

# logging and client
handler = logging.FileHandler("log", encoding="UTF-8")
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def main():
    """start client"""
    token = get_token()
    client.run(token, log_handler=handler, log_level=logging.DEBUG)

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
            await message.channel.send(GENERIC_ERROR_MESSAGE)
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
        case "reverse":
            await reverse(text, channel)
        case "peanut":
            await peanut(text, channel)
        case "ask":
            await ask(text, channel)

async def reverse(text, channel):
    """send back reversed text"""
    if text == "":
        await channel.send(
            f"{USAGE_MESSAGE} {BOT_PREFIX} reverse {YOUR_MESSAGE}")
        return
    await channel.send(text[::-1])

async def peanut(text, channel):
    """replace random letters with the peanuts emoji"""
    text_length = len(text)
    if text_length == 0:
        await channel.send(
            f"{USAGE_MESSAGE} {BOT_PREFIX} peanut {YOUR_MESSAGE}")
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
        await channel.send(f"{USAGE_MESSAGE} {BOT_PREFIX} ask {YOUR_MESSAGE}")
        return
    if random.random() >= 0.5:
        await channel.send("Yes.")
    else:
        await channel.send("No.")


if __name__ == "__main__":
    main()
