from discord.utils import get
import discord
import asyncio
from discord.ext import commands

bot = discord.Client(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("ready")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if 'WeirdoFish is a better builder' in message.content:
        await message.channel.send('Hapu_E is on the way to you')
        
@bot.event
async def on_message(message):
    if "Maybe our Parcade Bot wants to get help with Building" in message.content:
        await message.channel.send("I surely could need some help with building, thanks for asking ben")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if 'I will team up with the Parcade Bot' in message.content:
        await message.channel.send('okay sure')

bot.run('ID')
