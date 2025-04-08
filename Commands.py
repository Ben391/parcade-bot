import mysql.connector
import discord
import random
from socket import timeout
from socket import gaierror
from operator import itemgetter
import os
import sys

from discord import Member, Guild, channel
from discord.ext import commands
from datetime import datetime, time, timedelta
from math import floor
from mcstatus import MinecraftServer

bot = commands.Bot(command_prefix=commands.when_mentioned_or("pc ", "pc"), intents=discord.Intents.all())
bot.remove_command('help')

server_id = "ID"
test_channel_id = "ID"
test_message_id = "ID"

announcement_role_id = "ID"
update_role_id = "ID"
network_status_id = "ID"

default_role_id = "ID"
gold_role_id = "ID"
vip_role_id = "ID"


def dbconnection():
    playerdb = mysql.connector.connect(
        host="HOST",
        user="USER",
        password="PW",
        database="DB")
    return playerdb


def rank_color(NAME, playerdb):
    playerdb = dbconnection()
    cursor = playerdb.cursor()  # DATABASE COMMAND
    sql = 'SELECT parent FROM permissions_inheritance WHERE child = %s'
    val = (NAME,)
    cursor.execute(sql, val)
    rank_sql = cursor.fetchall()
    playerdb.close()
    code = 0x003275

    if len(rank_sql) == 0:
        code = 0x003275
    else:
        if rank_sql[0][0] == "Owner":  # DIFFERENT RANK CODES
            code = 0xFC9233

        if rank_sql[0][0] == "Admin":
            code = 0xe72b21

        if rank_sql[0][0] == "Management":
            code = 0xbf1111

        if rank_sql[0][0] == "Developer":
            code = 0xc26600

        if rank_sql[0][0] == "Moderator":
            code = 0xbd57e9

        if rank_sql[0][0] == "Builder":
            code = 0x1d7940

        if rank_sql[0][0] == "VIP":
            code = 0x65f3ff

        if rank_sql[0][0] == "GOLD":
            code = 0x966a0c

        if rank_sql[0][0] == "default":
            code = 0x003275


    return code

@bot.event
async def on_ready():
    admin_log = bot.get_channel(790006799797321749)
    await admin_log.send('[Parcade Commands] is online.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Couldn't find the command. Type `pchelp` for a list of commands")


@bot.command()
async def help(ctx):
    embed = discord.Embed(
                    title = "**⟪ ParcadeBot Help Page ⟫**",
                    description = 
                    'Bot Prefix: `pc`\n'
                    'like `pchelp` or `pc help`'
                    '\n\n📊 **STATS HELP**'
                    '\n\n`pc statshelp` - Shows all Stats Commands'
                    '\n\n🔗 **LINK HELP**'
                    '\n\n`pc linkhelp` - Shows all Link Commands'
                    '\n\n🕵️‍♂ **PROFILE HELP**'
                    '\n\n`pc profilehelp` - Shows all Stats Commands',
                    color = 0xFFFFFF)
    embed.set_footer(text='● Parcade Commands ●')
    await ctx.send(embed=embed)


@bot.command()
async def statshelp(ctx):
    embed = discord.Embed(
                title = "**⟪ Stats Help Page ⟫**",
                description = 
                'Bot Prefix: `pc`\n'
                'like `pchelp` or `pc help`'
                '\n\n🏃🏻‍♀ **PARKOUR COMMANDS**'
                '\n\n`pc stats <name>` - Parkour Total Stats of player'
                '\n`pc lbpos <map> <position>` - Leaderboard position of a specific map'
                '\n`pc pb <name> <map>` - Personal best of a player on a specific map'
                '\n\n🐉 **DRAGON ESCAPE COMMANDS**'
                '\n\n`pc destats <name>` - Dragon Escape Stats of a player'
                '\n\nMore is coming soon...',
                color = 0xFFFFFF)
    embed.set_footer(text='● Parcade Commands ●')
    await ctx.send(embed=embed)


@bot.command()
async def linkhelp(ctx):
    embed = discord.Embed(
            title = "**⟪ Link Help Page ⟫**",
            description = 
            'Bot Prefix: `pc`\n'
            'like `pchelp` or `pc help`'
            '\n\nYou can link your Discord Account with your Minecraft Account. '
            'In order to do that, you join our Minecraft Server Parcade (IP: Parcade.net) and type /linkdiscord. '
            'This will generate you a 7 digit code. Do not share the code! Go to this channel and type the link '
            'command below.'
            '\n\n🔗 **LINK COMMANDS**'
            '\n\n`pc link <code>` - Link your Discord Account with your Minecraft Account'
            '\n`pc linkreload` - Reload your Link between Discord and Minecraft',
            color = 0xFFFFFF)
    embed.set_footer(text='● Parcade Commands ●')
    await ctx.send(embed=embed)
    
@bot.command()
async def profilehelp(ctx):
    embed = discord.Embed(
            title = "**⟪ Profile Help Page ⟫**",
            description = 
            'Bot Prefix: `pc`\n'
            'like `pchelp` or `pc help`'
            '\n\n🕵️‍♂ **PROFILE COMMANDS**'
            '\n\n`pc profile <name>` - View a profile of a specific player',
            color = 0xFFFFFF)
    embed.set_footer(text='● Parcade Commands ●')
    await ctx.send(embed=embed)


@bot.command(aliases=["stats", "sts"])
async def parstats(ctx, NAME):
    playerdb = dbconnection()
    cursor = playerdb.cursor()
    sql = "SELECT pc_players.player_name, joins, leaves, deaths, finishes, resets, checkpoints, playtime, " \
          "pc_players.player_uuid FROM parkour_stats INNER JOIN pc_players " \
          "ON pc_players.player_uuid = parkour_stats.player_uuid WHERE player_name = %s"
    val = (NAME,)
    cursor.execute(sql, val)
    stats = cursor.fetchall()
    print(stats)

    if len(stats) == 0:
        await ctx.send("This user has not played Parkour. Please enter a different username.")
        return

    playtime_milli = stats[0][7]  # PLAYTIME CONVERT
    minutes = playtime_milli / (1000 * 60) % 60
    hours = playtime_milli / (1000 * 60 * 60) % 24
    days = playtime_milli / (1000 * 60 * 60 * 24)

    minutes = str(floor(minutes))
    hours = str(floor(hours))
    days = str(floor(days))

    playtime = days + ' Days ' + hours + ' Hours ' + minutes + ' Minutes'

    print(type(stats[0][8]))

    embed = discord.Embed(title='Statistics of ' + NAME,  # STATS EMBED
                          color=rank_color(stats[0][8], playerdb),
                          description='Parkour Player Statistics')
    embed.add_field(name='Joins:', value=stats[0][1],
                    inline=False)
    embed.add_field(name='Leaves:', value=stats[0][2],
                    inline=False)
    embed.add_field(name='Deaths:', value=stats[0][3],
                    inline=False)
    embed.add_field(name='Finishes:', value=stats[0][4],
                    inline=False)
    embed.add_field(name='Resets:', value=stats[0][5],
                    inline=False)
    embed.add_field(name='Checkpoints:', value=stats[0][6],
                    inline=False)
    embed.add_field(name='Playtime:', value=playtime,
                    inline=False)
    embed.set_thumbnail(url='https://crafatar.com/avatars/' + stats[0][8] + '/?size=60&overlay')
    embed.set_footer(text='Parcade.net')
    await ctx.send(embed=embed)
    playerdb.close()


@parstats.error
async def parstats_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please enter a username. Usage: `pcstats <username>`')


@bot.command(aliases=["dests"])
async def destats(ctx, NAME):
    await ctx.send("Dragon Escape Stats will soon be merged with Parkour Stats")
    print(NAME)


@destats.error
async def destats_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please enter a username. Usage: `pcdestats <username>`')


@bot.command()
async def link(ctx, CODE):
    playerdb = dbconnection()
    playerdb.commit()  # Datenbanken reload
    cursor = playerdb.cursor()  # SQL Cursor einrichten

    # GET MC-NAME AND MC-UUID via DISCORD-CODE

    sql = "SELECT player_uuid, player_name FROM pc_players WHERE discord_code = %s"  # Player UUID und Name nehmen
    cursor.execute(sql, (CODE,))  # Cursor ausführen
    result1 = cursor.fetchall()  # Ergebnisse von der SQL Suche festhalten als "result1"
    playerdb.close()

    # NO CODE FOUND IN DATABASE
    if len(result1) == 0:  # Sollte kein Discord_Code gefunden werden
        await ctx.send('The code is wrong or expired.')  # Discord Bot Nachricht
        return  # ???? STOP EXECUTION OF COMMAND IF CODE CAN'T BE FOUND

    # SET DISCORD-UUID IN DATABASE via DISCORD-CODE
    playerdb = dbconnection()
    cursor = playerdb.cursor() 
    sql2 = "UPDATE pc_players SET discord_uuid = %s WHERE discord_code = %s"  # discord_uuid einfügen
    val2 = (ctx.author.id, CODE)  # die Discord uuid vom Command Verfasser nehmen
    cursor.execute(sql2, val2)
    playerdb.commit()
    playerdb.close()

    # DATA FOR PLAYER THAT WAS FOUND via DISCORD-CODE
    playerUUID = result1[0][0]
    playerName = result1[0][1]

    # NICK PLAYER IN DISCORD
    try:
        await ctx.author.edit(nick=playerName)  # Dem Spieler den aus der Datenbank entnommenden namen geben
    except Exception as e:
        admin_log = bot.get_channel(790006799797321749)
        await admin_log.send(e)
        pass

    # GET RANK FROM PERMISSIONS DATABASE via MC-UUID
    # THIS CALL SHOULD BE MADE TOGETHER WITH THE FIRST CALL. NO NEED FOR 2 DATABASE QUERIES
    playerdb = dbconnection()
    cursor = playerdb.cursor() 
    sql = "SELECT parent FROM permissions_inheritance WHERE child = %s"  # den der UUID entsprechenden Rank nehmen
    val = (playerUUID,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    playerdb.close()

    # NO RANK FOR THIS MC-UUID --> DEFAULT RANK
    if len(result) == 0:  # Sollte bei der UUID kein rank eingetragen sein
        guild: discord.Guild = bot.get_guild(server_id)  # server uuid als "guild" festlegen
        role: discord.Role = guild.get_role(default_role_id)  # default rank ID als "role" festlegen
        await ctx.author.add_roles(role, reason='default')  # dem Verfasser die default role geben
        await ctx.send('You have successfully linked your Minecraft account.')
        removeCode(CODE, playerdb)
        return  # ???? STOP EXECUTION OF COMMAND IF LINK WAS SUCCESFUL

    # RANK WAS FOUND
    rank = result[0][0]

    guild: discord.Guild = bot.get_guild(server_id)  # Alle Rollen die wir haben festlegen
    default_role: discord.Role = guild.get_role(default_role_id)
    gold_role: discord.Role = guild.get_role(gold_role_id)
    vip_role: discord.Role = guild.get_role(vip_role_id)
    try:
        if rank == 'GOLD':
            await ctx.remove_roles(default_role, reason='not default')
            await ctx.remove_roles(vip_role, reason='not vip')
            await ctx.add_roles(gold_role, reason='gold')
        if rank == 'VIP':
            await ctx.add_roles(vip_role, reason='vip')
            await ctx.remove_roles(default_role, reason='not default')
            await ctx.remove_roles(gold_role, reason='not gold')
        if rank == 'default':
            await ctx.add_roles(default_role, reason='default')
            await ctx.remove_roles(gold_role, reason='gold')
            await ctx.remove_roles(vip_role, reason='not vip')
    except AttributeError:
        print('Attribute Error')
        pass
    except discord.errors.Forbidden:
        pass
    except Exception as e:
        admin_log = bot.get_channel(790006799797321749)
        await admin_log.send(e)
        pass
    removeCode(CODE, playerdb)
    playerdb.close()
    await ctx.send('You have successfully linked your Minecraft account.')


def removeCode(CODE, playerdb):
    cursor = playerdb.cursor()
    sql3 = 'UPDATE pc_players SET discord_code = NULL WHERE discord_code = %s'  # code entfernen
    val3 = (CODE,)
    print(CODE)
    cursor.execute(sql3, val3)


@link.error
async def link_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please type your code in order to link your account. Usage: `pclink <code>`')


@bot.command()
async def pb(ctx, NAME, MAP):
    playerdb = dbconnection()
    cursor = playerdb.cursor()
    sql = "SELECT pc_players.player_name, personalBestID, uuid, " \
          "arenaName, time, date FROM parkour_personalBests " \
          "INNER JOIN pc_players ON pc_players.player_uuid = parkour_personalBests.uuid WHERE player_name = " \
          "%s AND arenaName = %s GROUP BY personalBestID ORDER BY time LIMIT 1"
    val = (NAME, MAP)
    cursor.execute(sql, val)
    personal_best = cursor.fetchall()

    print(personal_best)

    if len(personal_best) == 0:
        await ctx.send('This player has no Personal Best on this map.')

    date = personal_best[0][5] / 1000
    date_time = datetime.fromtimestamp(date)
    rightdate = date_time.strftime("%m/%d/%Y, %H:%M:%S")

    milli_time = personal_best[0][4]
    date = datetime.fromtimestamp(milli_time / 1000.0)
    date = date.strftime('%M:%S.%f')[:-3]

    embed = discord.Embed(title='Statistics of ' + NAME,
                          color=rank_color(personal_best[0][2], playerdb),
                          description='Personal Best on Parkour')
    embed.add_field(name='Arena:',
                    value=personal_best[0][3].capitalize(),
                    inline=False)
    embed.add_field(name='Time:',
                    value=date,
                    inline=False)
    embed.add_field(name='Date:',
                    value=rightdate,
                    inline=False)
    embed.set_thumbnail(url='https://crafatar.com/avatars/' + personal_best[0][2] + '/?size=60&overlay')
    embed.set_footer(text='Parcade.net')
    await ctx.send(embed=embed)
    playerdb.close()


@pb.error
async def parpb_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please enter a name and a username. Usage: `pcparpb <username>`')


@bot.command()
async def linkreload(ctx):
    playerdb = dbconnection()
    cursor = playerdb.cursor()
    playerdb.commit()

    sql2 = "SELECT permissions_inheritance.parent, player_name FROM pc_players INNER JOIN " \
           "permissions_inheritance ON child = player_uuid WHERE discord_uuid = %s"  # Rank, Name, UUID Discord UUID

    # Tabelle nehmen
    DISCORDID = int(ctx.author.id)
    val2 = (DISCORDID,)
    cursor.execute(sql2, val2)
    data = cursor.fetchall()

    rank = data[0][0]
    playerName = data[0][1]

    # PLAYER NAME CHANGE
    try:
        if ctx.author.display_name != playerName:  # Sollte der Name des Spielers nicht mit der datenbank übereinstimmen
            await ctx.author.edit(nick=playerName)  # discord user name wird geändert
    except AttributeError:
        print('Attribute Error')  # Attribute Error treten auf wenn keine UUID eingetragen ist und sind nicht
        # wirklich zu verhindern
    except discord.errors.Forbidden:
        print('Missing Permissions')  # Missing Permissions tritt auf, weil der Name von Leuten mit Administrator
        # Rechten nicht geändert werden kann
    except TypeError:
        print('TypeError')  # Ein Problem mit ctx.author.display_name was wohl nicht anders zu beheben ist.
    # WENN DER TYPEERROR WIRKLICH NUR MIT ctx.author.display_name ZU TUN HAT, MÜSSTE DIE EXCEPTION HIER AUCH OK SEIN

    guild = bot.get_guild(server_id)  # Server UUID als "guild" festlegen

    default_role: discord.Role = guild.get_role(default_role_id)
    gold_role: discord.Role = guild.get_role(gold_role_id)
    vip_role: discord.Role = guild.get_role(vip_role_id)

    try:
        print(rank)
        if rank == 'GOLD':
            await ctx.author.remove_roles(default_role, reason='not default')
            await ctx.author.remove_roles(vip_role, reason='not vip')
            await ctx.author.add_roles(gold_role, reason='gold')
        if rank == 'VIP':
            await ctx.author.add_roles(vip_role, reason='vip')
            await ctx.author.remove_roles(default_role, reason='not default')
            await ctx.author.remove_roles(gold_role, reason='not gold')
        if rank == 'default':
            await ctx.author.add_roles(default_role, reason='default')
            await ctx.author.remove_roles(gold_role, reason='gold')
            await ctx.author.remove_roles(vip_role, reason='not vip')
    except AttributeError:
        print('Attribute Error')

    await ctx.send('You have successfully updated your link.')
    playerdb.close()


@bot.command()
@commands.has_permissions(administrator=True)
async def instantcheck(ctx):
    playerdb = dbconnection()
    playerdb.commit()
    cursor = playerdb.cursor()
    sql2 = "SELECT permissions_inheritance.parent, player_name, discord_uuid FROM pc_players INNER JOIN " \
           "permissions_inheritance ON child = player_uuid"  # Rank, Name, UUID Discord UUID Tabelle nehmen
    cursor.execute(sql2)
    result = cursor.fetchall()

    print(result)

    for data in result:
        rank = data[0]
        playerName = data[1]
        discordUUID = data[2]

        # NO DISCORD-UUID FOUND FOR THIS PLAYER --> CHECK NEXT PLAYER (continue)
        if discordUUID is None:
            continue

        guild = bot.get_guild(server_id)  # server uuid
        member: discord.Member = guild.get_member(int(discordUUID))  # member wird die DiSCORD ID zugeteilt
        print(playerName)
        print(discordUUID)

        try:
            if member.display_name != playerName:  # Sollte der Name nicht dem Namen der Datenbank entsprechen
                await member.edit(nick=playerName)  # Der Name wird geändert
        except AttributeError:
            print('Attribute Error')
        except discord.errors.Forbidden:
            print('Permission Error')
            continue

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
            print('Permission Error')

    await ctx.send('Updated Ranks and Usernames from the Database.')
    playerdb.close()


@instantcheck.error
async def instantcheck(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send("You don't have permissions to execute this command.")


@bot.command()
async def status(ctx):
    server = MinecraftServer.lookup("parcade.net")

    try:
        status = server.status()
        print("The server replied in {0} ms".format(status.players.online, status.latency))
        # ONLINE MESSAGE
        await ctx.send("Parcade is online.")
    except gaierror:
        await ctx.send('Parcade is offline.')

    except timeout:

        # OFFLINE MESSAGE
        await ctx.send('Parcade is offline.')


@bot.command(aliases=["lbp", "lbpos"])
async def leaderboardposition(ctx, ARENA, PLACE, KIT="none"):
    
    playerdb = dbconnection()
    cursor = playerdb.cursor()
    sql = "CALL parkour_kit_leaderboard(%s, %s, 100)"
    val = (ARENA, KIT)
    iterable = cursor.execute(sql, val, multi=True)
    item = next(iterable)
    map_placement = item.fetchall()
    playerdb.close()

    if PLACE is not None:
        PLACE_PY = int(PLACE) - 1

        player_name = map_placement[PLACE_PY][1]
        print(player_name)
        player_uuid = map_placement[PLACE_PY][0]
        print(player_uuid)

        # MILLI TO TIMER CONVERT
        milli_time = map_placement[PLACE_PY][2]
        date = datetime.fromtimestamp(milli_time / 1000.0)
        convert_time = date.strftime('%M:%S.%f')[:-3]

        print(convert_time)

        # DATE CONVERT
        time = map_placement[PLACE_PY][3] / 1000
        date_time = datetime.fromtimestamp(time)
        rightdate = date_time.strftime("%m/%d/%Y, %H:%M:%S")

        print(type(map_placement[PLACE_PY][3]))

        print(rightdate)
        #  (rank_color(player_uuid, playerdb))
        uuid = map_placement[PLACE_PY][0]
        color = rank_color(uuid, playerdb)

        # EMBED FOR POSITION
        if KIT == "none":
            embed = discord.Embed(title='#' + PLACE + ' on ' + ARENA.capitalize(),
                                color=color)
            embed.add_field(name='Name:',
                            value=player_name,
                            inline=False)
            embed.add_field(name='Time:',
                            value=convert_time,
                            inline=False)
            embed.add_field(name='Date',
                            value=rightdate,
                            inline=False)
            embed.set_thumbnail(url='https://crafatar.com/avatars/' + player_uuid + '/?size=60&overlay')
            embed.set_footer(text='Parcade.net')
            await ctx.send(embed=embed)

            playerdb.close()
            
        else: 
            embed = discord.Embed(title='#' + PLACE + ' on ' + ARENA.capitalize(),
                                color=color)
            embed.add_field(name='Name:',
                            value=player_name,
                            inline=False)
            embed.add_field(name='Time:',
                            value=convert_time,
                            inline=False)
            embed.add_field(name='Date',
                            value=rightdate,
                            inline=False)
            embed.add_field(name='Kit',
                            value=KIT,
                            inline=False)
            embed.set_thumbnail(url='https://crafatar.com/avatars/' + player_uuid + '/?size=60&overlay')
            embed.set_footer(text='Parcade.net')
            await ctx.send(embed=embed)

            playerdb.close()


@bot.command()
async def profile(ctx, NAME):
    playerdb = dbconnection()
    # PC Players Database SQL
    cursor = playerdb.cursor()
    sql = 'SELECT pc_players.player_name, uuid, cubics, parkourXp FROM cubics_data INNER JOIN pc_players ' \
          'ON player_uuid = uuid WHERE player_name = %s'
    val = (NAME,)
    cursor.execute(sql, val)
    pc_players = cursor.fetchall()

    # Friends Database SQL
    sql2 = 'SELECT player_name, player_uuid, last_online FROM fr_players WHERE player_uuid = %s'
    val = (pc_players[0][1],)
    cursor.execute(sql2, val)
    friends_sql = cursor.fetchall()
    print(friends_sql)
    if len(friends_sql) == 0:
        last_online = "Unknown"
        print(last_online)
    else:
        last_online = friends_sql[0][2]

    # Rank Database SQL
    sql3 = 'SELECT parent FROM permissions_inheritance WHERE child = %s'
    val = (pc_players[0][1],)
    cursor.execute(sql3, val)
    rank_sql = cursor.fetchall()

    if len(rank_sql) == 0:
        rank = "Member"
        print(rank)
    else:
        rank = str(rank_sql[0][0])

    embed = discord.Embed(title='Profile of ' + pc_players[0][0],
                          color=rank_color(pc_players[0][1], playerdb))
    print("...")
    embed.add_field(name='Rank:',
                    value=rank,
                    inline=False)
    embed.add_field(name='Cubics:',
                    value=pc_players[0][2],
                    inline=False)
    embed.add_field(name='Experience:',
                    value=pc_players[0][3],
                    inline=False)
    embed.add_field(name='Last Online',
                    value=last_online,
                    inline=False)
    print("...")
    embed.set_thumbnail(url='https://crafatar.com/avatars/' + pc_players[0][1] + '/?size=60&overlay')
    embed.set_footer(text='Parcade.net')
    await ctx.send(embed=embed)
    playerdb.close()
@bot.command()
async def restart(ctx):
    if ctx.channel.id == 1074791727208091689:
        if ctx.author.id == 173779204666556417 or ctx.author.id == 280654220254773248 or ctx.author.id == 191474138450362369 or ctx.author.id == 356257712750985218:
            await ctx.send("Restarting the bot...")
            os.execv(sys.executable, ["python3"] + sys.argv)
        else:
            await ctx.send("You do not have permission to use this command.")
        
@bot.command(aliases=["uppa", "upgradep"])
async def upgrade_particle(ctx, message_id):
    channel = bot.get_channel(1074791727208091689)
    try:
        message = await channel.fetch_message(message_id)
        reactions = message.reactions
        reacted_users = set()
        for reaction in reactions:
            async for user in reaction.users():
                reacted_users.add(user.id)
        
        playerdb = dbconnection()
        cursor = playerdb.cursor()
        
        reacted_users_placeholder = ', '.join([str(user) for user in reacted_users])
        sql_uuids = "SELECT player_uuid FROM pc_players WHERE discord_uuid IN ({})"
        cursor.execute(sql_uuids.format(reacted_users_placeholder))
        
        reacted_uuids = [result[0] for result in cursor.fetchall()]
        
        for uuid in reacted_uuids:
            ctx.send(uuid)
            
    except discord.NotFound:
        await ctx.send("Message not found or ID from the wrong channel.")
        return

bot.run('ID')
