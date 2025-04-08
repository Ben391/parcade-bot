import mysql.connector
import discord
import pytz
import os
import sys
import schedule
import asyncio
from datetime import datetime, timezone, timedelta


from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or("schedule"), intents=discord.Intents.all())

server_id = "ID"
test_channel_id = "ID"
test_message_id = "ID"

announcement_role_id = "ID"
update_role_id = "ID"
network_status_id = "ID"

default_role_id = "ID"
gold_role_id = "ID"
vip_role_id = "ID"

h_builder_chat = "ID"
checkups_chat = "ID"

def dbconnection():
    playerdb = mysql.connector.connect(
        host="HOST",
        user="USER",
        password="PW",
        database="DB")
    return playerdb

@bot.event
async def on_ready():
    admin_log = bot.get_channel(790006799797321749)
    await admin_log.send('[Parcade Routines] is online. (Please only restart if really necessary)')
    
    cet_tz = pytz.timezone("CET")
    
    schedule.every(600).seconds.do(dailycheck_wrp)
    schedule.every().saturday.at("22:00").do(checkups_wrp)
    schedule.every().sunday.at("00:00").do(trello_wrp)
    
    while True:
        await asyncio.sleep(1)
        schedule.run_pending()

        now = datetime.now(tz=pytz.timezone("CET"))
        for job in schedule.jobs:
            if job.tags and (job.tags in ['checkups', 'trello']):
                next_run = job.next_run.astimezone(pytz.timezone("CET"))
                if now >= next_run:
                    asyncio.create_task(job.func())
                    job.last_run = now
                    job._schedule_next_run()

@bot.command()
async def restart(ctx):
    if ctx.channel.id == 1061650280850137138:
        if ctx.author.id == 173779204666556417 or ctx.author.id == 280654220254773248 or ctx.author.id == 191474138450362369 or ctx.author.id == 356257712750985218:
            await ctx.send("Restarting the bot...")
            os.execv(sys.executable, ["python3"] + sys.argv)
        else:
            await ctx.send("You do not have permission to use this command.")

def dailycheck_wrp():
    asyncio.create_task(dailycheck())

def checkups_wrp():
    asyncio.create_task(checkups())

def trello_wrp():
    asyncio.create_task(trello())

async def trello():
    channel = await bot.fetch_channel(h_builder_chat)
    await channel.send(
        f'Please update Trello. @everyone'
    )
    
async def checkups():
    channel = await bot.fetch_channel(checkups_chat)
    await channel.send(
        f'Please give a little sum up of what you did this week. @everyone'
    )

async def dailycheck():
    playerdb = dbconnection()
    playerdb.commit()
    cursor = playerdb.cursor()
    sql2 = "SELECT permissions_inheritance.parent, player_name, discord_uuid FROM pc_players INNER JOIN " \
            "permissions_inheritance ON child = player_uuid"
    cursor.execute(sql2)
    result = cursor.fetchall()
    playerdb.close()

    for data in result:
        rank = data[0]
        playerName = data[1]
        discordUUID = data[2]

        # NO DISCORD_UUID FOUND FOR THIS PLAYER --> CHECK NEXT PLAYER (continue)
        if discordUUID is None:
            continue

        guild = bot.get_guild(server_id)
        member: discord.member = guild.get_member(int(discordUUID))
        print(member)
        try:
            if member.display_name != playerName:
                await member.edit(nick=playerName)
        except AttributeError:
            print('Attribute Error')

        except discord.errors.Forbidden:
            pass

        default_role: discord.Role = guild.get_role(default_role_id)
        gold_role: discord.Role = guild.get_role(gold_role_id)
        vip_role: discord.Role = guild.get_role(vip_role_id)

        try:
            print(rank)
            if rank == 'GOLD':
                await member.remove_roles(default_role, reason='not default')
                await member.remove_roles(vip_role, reason='not vip')
                await member.add_roles(gold_role, reason='gold')
            if rank == 'VIP':
                await member.add_roles(vip_role, reason='vip')
                await member.remove_roles(default_role, reason='not default')
                await member.remove_roles(gold_role, reason='not gold')
            if rank == 'default':
                await member.add_roles(default_role, reason='default')
                await member.remove_roles(gold_role, reason='gold')
                await member.remove_roles(vip_role, reason='not vip')
        except AttributeError:
            print('Attribute Error')
        except discord.errors.Forbidden:
            pass

bot.run('ID')
