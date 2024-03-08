from discord.ext import commands
import discord
import dotenv
import logging
import os
import asyncio


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
dotenv.load_dotenv(r"D:\Workspace\Aiya_Bot\myData.env")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

# Use commands.Bot instead of discord.bot
bot = commands.Bot(command_prefix='-', intents=intents,)

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    await ctx.message.delete()

# Auto Loader
async def loader():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"- {file}", "loaded succefuly")


asyncio.run(loader())
# On_ready event
@bot.event
async def on_ready():
    print("-- "*20)
    print("Aiya is ready to use!" )
    await bot.change_presence(activity=discord.Game("With Yosef!!"),status=discord.Status.idle)

TOKEN=os.getenv("token")
bot.run(TOKEN, log_handler=handler)