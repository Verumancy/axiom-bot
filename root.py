import sys
sys.dont_write_bytecode = True
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import configs
import dataHandler

class axiomBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents)

    async def setup_hook(self) -> None:
        pass

client = axiomBot()

async def main():
    await loadCogs()
    await client.start(token)

@client.event
async def on_ready():
    print("Bot is online")
    await setActivityStatus()
    commands = client.tree.get_commands()
    print("---Commands---")
    for x in commands:
        print(x.name)

#Import token and mongo connection URL from text files
with open("token.txt") as f: token = f.readline()

#Set activity status based on type and message
#Types:1:Playing,2:Streaming,3:Listening,4:Watching,5:Competing
activityStatusMessage = "the market crash"
activityStatusType = 4



async def loadCogs():
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"{filename} loaded as cog")
    
async def setActivityStatus():
    match activityStatusType:
        case 1:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=activityStatusMessage))
            print(f"Set staus to 'Playing {activityStatusMessage}'")
        case 2:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name=activityStatusMessage))
            print(f"Set staus to 'Streaming {activityStatusMessage}'")
        case 3:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activityStatusMessage))
            print(f"Set staus to 'Listening to {activityStatusMessage}'")
        case 4:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activityStatusMessage))
            print(f"Set staus to 'Watching {activityStatusMessage}'")
        case 5:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=activityStatusMessage))
            print(f"Set staus to 'Competing in {activityStatusMessage}'")

@client.command()
@commands.is_owner()
async def sync(ctx):
    print("Attempting Sync")
    try:        
        await client.tree.sync()

        commands = client.tree.get_commands()
        print("---Syncrd Commands---")
        for x in commands:
            print(x.name)
    except Exception as e:
        print(e)

asyncio.run(main())