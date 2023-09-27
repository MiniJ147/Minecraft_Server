# bot.py
import os
import socket

import discord
from discord.ext import commands
#developing
from dotenv import load_dotenv

#do not include when shipping 
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#do not include when code visiable 
#TOKEN = 'TOKEN KEY FROM ENV'

REQUEST_SERVER_UP = 1
REQUEST_SERVER_DOWN = 2
REQUEST_SERVER_STATUS = 3

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

def handle_request(request):
    s = socket.socket()
    s.connect(("127.0.0.1",25566))

    s.send(request.to_bytes(2,'big'))

    result = s.recv(2048)
    print(result)

    s.close()

    return result

@bot.event
async def on_ready():
    print("online")
    await bot.change_presence(activity=discord.Game('Server Down'))


@bot.command(name="up")
async def up(ctx):
    await ctx.send("Sending Server Up")
    message = handle_request(REQUEST_SERVER_UP)
    await ctx.send("[SERVER] "+message.decode("utf-8"))


    if handle_request(REQUEST_SERVER_STATUS) == b'UP':
        await bot.change_presence(activity=discord.Game('Server Running!'))
    else:
        await bot.change_presence(activity=discord.Game('Server Down'))


@bot.command(name="down")
async def down(ctx):
    await ctx.send("Sending Server Down")
    message = handle_request(REQUEST_SERVER_DOWN)
    await ctx.send("[SERVER] "+message.decode("utf-8"))


    if handle_request(REQUEST_SERVER_STATUS) == b'UP':
        await bot.change_presence(activity=discord.Game('Server Running!'))
    else:
        await bot.change_presence(activity=discord.Game('Server Down'))
    

bot.run(TOKEN)
