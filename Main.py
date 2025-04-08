from discord.utils import get
import discord
import asyncio
import os
import sys
import json
import atexit

from mcstatus import JavaServer
from discord.ext import commands

with open("/srv/bot/bot_values.json", "r") as f:
    data = json.load(f)

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=discord.Intents.all())

ADMIN_LOG = "ID"

@bot.event
async def on_ready():
    admin_log = bot.get_channel(ADMIN_LOG)
    await admin_log.send('[Parcade Main] is online.')
    update_time = data["bot_values"][0]
    bot.loop.create_task(status_task(str(update_time['update_value'])))  

async def status_task(update_time):
    admin_log = bot.get_channel(ADMIN_LOG)
    while True:
        try:
            await bot.change_presence(activity=discord.Game('https://invite.gg/Parcade'), status=discord.Status.online)
            await asyncio.sleep(30)
            try: 
                server = JavaServer.lookup("parcade.net")
                status = server.status()
                await bot.change_presence(activity=discord.Game("{0} Players Online".format(status.players.online)),
                                        status=discord.Status.online)
            except asyncio.TimeoutError as a:
                await admin_log.send(f"Server lookup timed out: {a}")
            except Exception as e:
                await admin_log.send(f"Error occurred: {e}")
            await asyncio.sleep(30)

            if update_time != "none":
                await bot.change_presence(activity=discord.Game("Update: " + update_time),
                                        status=discord.Status.online)
                await asyncio.sleep(30)
        except asyncio.exceptions.TimeoutError as a:
            await admin_log.send(f"Asyncio Timeout: {a}")
            pass
        #schedule.run_pending()

@bot.command()
async def restart(ctx):
    if ctx.channel.id == "ID":
        if ctx.author.id == "ID" or ctx.author.id == "ID" or ctx.author.id == "ID" or ctx.author.id == "ID":
            await ctx.send("Restarting the bot...")
            os.execv(sys.executable, ["python3"] + sys.argv)
        else:
            await ctx.send("You do not have permission to use this command.")
@bot.command()
async def update(ctx, update=None):
    if ctx.author.id == "ID" or ctx.author.id == "ID" or ctx.author.id == "ID" or ctx.author.id == "ID":
        data["bot_values"][0]["update_value"] = update
        
        with open("/srv/bot/bot_values.json", "w") as f:
            json.dump(data, f)
        await ctx.send("Update Date set ")
    else:
        await ctx.send("You do not have permission to use this command.")
        
        
bot.run('ID')
