import asyncio
import discord
import mysql.connector
import requests
import re
import shutil
import asyncio
import os
import sys

from math import floor
from discord.ext import commands
from datetime import *
from discord import Embed, member
from discord.ui.button import Button, ButtonStyle
from discord.ui import View

bot = discord.Client(intents=discord.Intents.all())

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!+"), intents=intents)

GUILD_ID = "ID"
TICKET_CHANNEL = "ID"
SUPPORT_CATEGORY_ID = "ID"
MODERATOR_ID = "ID"
GUIDE_ID = "ID"
INFO_CATEGORY_ID = "ID"
CLOSED_CATEGORY_ID = "ID"
INFO_CHANNEL_ID = "ID"
ADMIN_CHANNEL_LOG = "ID"

@bot.event
async def on_ready():
    print("READY")

def connect():
    playerdb = mysql.connector.connect(
        host="HOST",
        user="USER",
        password="PW",
        database="DB",
    )
    return playerdb

def check_perms(user, perms):
    print("check perms")
    has_perms = False
    playerdb = connect()
    playerdb.commit()
    cursor = playerdb.cursor()
    sql = ("SELECT discord_id FROM discord_user_permissions WHERE discord_id = %s AND permissions = %s")
    val = (user, perms)
    cursor.execute(sql, val)
    list_perms = cursor.fetchall()
    playerdb.close() 
    
    if len(list_perms) > 0:
        print("has perms")
        has_perms = True
        return has_perms
    
    else:
        print("has no perms")
        return has_perms

def get_last_ticket(user_id):
    playerdb = connect()
    playerdb.commit()
    cursor = playerdb.cursor()
    sql = ("SELECT ticket_date FROM discord_tickets WHERE user_id = %s ORDER BY ticket_date DESC LIMIT 1")
    val = (user_id,)
    cursor.execute(sql, val)
    ticket_date_list = cursor.fetchall()
    playerdb.close() 
    print(ticket_date_list)
    if len(ticket_date_list) > 0:
        ticket_date = ticket_date_list[0][0]
    else: 
        ticket_date = None
    return ticket_date

def set_ticket_number(user):
    # GENERATE UNIQUE TICKET NUMBER FOR CHANNEL NAME
    ticket_number = hash(user.id)%100000+1
    
    # CONNECT TO PARCADE DATABASE AND GET TICKET DATA
    playerdb = connect()
    playerdb.commit()
    cursor = playerdb.cursor()
    sql = "SELECT ticket_number, ticket_status, ticket_date user_id FROM discord_tickets WHERE ticket_number = %s ORDER BY ticket_date DESC LIMIT 1"
    val = (ticket_number,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    playerdb.close()  
    try:
        # CHECK IF UNIQUE TICKET NUMBER WAS USED BEFORE
        if result[0][0] != None:
            
            playerdb = connect()
            playerdb.commit()
            cursor = playerdb.cursor()
            sql = "SELECT user_id, ticket_status FROM discord_tickets WHERE user_id = %s ORDER BY ticket_status DESC"
            val = (user.id,)
            cursor.execute(sql, val)
            result = cursor.fetchall()
            playerdb.close()
            
            # ADD UP UNIQUE TICKET NUMBER TILL IT IS UNIQUE TO DATABASE
            while result[0][0] != None:
                ticket_number=ticket_number+len(result)
                playerdb = connect()
                playerdb.commit()
                cursor = playerdb.cursor()
                sql = "SELECT ticket_number, ticket_status FROM discord_tickets WHERE ticket_number = %s ORDER BY ticket_status DESC LIMIT 1"
                val = (ticket_number,)
                cursor.execute(sql, val)
                result = cursor.fetchall()
                playerdb.close()
                    
        else:
            print("Ticket ID reused")
    except IndexError:
        print("ID not in Database")
        
    return ticket_number

class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix=commands.when_mentioned_or("+"), intents=intents)
    async def setup_hook(self) -> None:
        self.add_view(Close())
        self.add_view(Application_Buttons())
        self.add_view(OpenAgain())
        self.add_view(Rule_Buttons())

bot = PersistentViewBot()

class Close(discord.ui.View):
    message = discord.Message
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1,10, commands.BucketType.member)
    @discord.ui.button(style=ButtonStyle.grey, label="CLOSE", emoji="❌", custom_id="close2")
    async def close_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        category = await bot.fetch_channel(CLOSED_CATEGORY_ID)
        await interaction.channel.edit(category=category)
        embed2 = discord.Embed(
            title="⟪ CLOSED TICKET ⟫",
            description=
            f"Your ticket got closed. This likely happened because of the following reasons: \n" 
            f"- you decided to close your ticket \n"
            f"- the topic has been resolved \n"
            f"- there hasn't been a reply from you in some time\n\n"
            f'If you feel like your case is not resolved, please click on the "Open Again" button. \n\n'
            f"Do not hesistate to open another ticket anytime soon."
            f"\n"
            f"Thank you for reaching out to our staff team!",
            color=discord.colour.Color.dark_grey(),
        )
        embed2.set_footer(text='● Parcade Ticket System ●')
        view = OpenAgain()
        close_message = await interaction.response.send_message(embed=embed2, view=view)
        view.message = close_message
        await interaction.message.delete()

class OpenAgain(discord.ui.View):
    message = discord.Message
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1,10, commands.BucketType.member)
    @discord.ui.button(style=ButtonStyle.green, label="OPEN AGAIN", emoji="✔️", custom_id="open_again")
    async def open_again_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.message.delete()
        category = await bot.fetch_channel(SUPPORT_CATEGORY_ID)
        await interaction.channel.edit(category=category)
        embed2 = discord.Embed(
            title="⟪ REOPENED TICKET ⟫",
            description=
            f"You have decided to reopen your ticket. We are happy to hear your input about the case. \n" 
            f'If you feel like your ticket has been resolved, please click on the "CLOSE" button. \n'
            f"As you wait, please be patient and make sure to be nice to our staff team.",
            color=discord.colour.Color.dark_grey(),
        )
        embed2.set_footer(text='● Parcade Ticket System ●')
        view = Close()
        close_message = await interaction.response.send_message(embed=embed2, view=view)
        view.message = close_message

class Application_Buttons(discord.ui.View):
    message = discord.Message
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(style=ButtonStyle.green, label="BUILDER", emoji="⛏", custom_id="builder_apply")
    async def builder_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        WeirdoFish_user = bot.get_user(int("ID"))
        Hapu_user = bot.get_user(int("ID"))
        embed=discord.Embed(
            title="Builder",
            description=
            f"Our Builders do exactly as you'd expect - they build. They spend countless hours "
            f"putting together high quality maps, hubs/spawns, event areas, and anything you " 
            f"can think of. They are able to work a team to complete large projects but also "
            f"perform solo with their own maps. Builders are certainly a riving force on our "
            f"server, so we'd love to have you! \n\n"
            f"**Tasks of a Builder**\n"
            f"- Build various types of maps using plugins such as WorldEdit and VoxelSniper alone or with other people \n"
            f"- Build larger maps with the team while getting along with everyone \n"
            f"- Review other builders' maps and help improve them \n"
            f"- Test maps before release to make sure they are built correctly \n"
            f"- Help out with the building side of various projects led by higher staff \n\n"
            f"---------------------------------------------------------------\n"
            f"Please respond in the following format:\n\n"
            f"Question 1: (Your answer)\n"
            f"Question 2: (Your answer)\n"
            f"...\n"
            f"---------------------------------------------------------------\n\n"
            f"**Question 1**\n"
            f"What is your Minecraft username?\n\n"
            f"**Question 2**\n"
            f"How old are you?\n"
            f"*(be honest, we will find out if you're not)\n\n"
            f"**Question 3**\n"
            f"Have you been punished on the Parcade Network before?\n"
            f'Please tell us what the punishment(s) was, or reply "none"\n\n'
            f"**Question 4**\n"
            f"Have you been staff on any other servers?\n"
            f"*If so, tell us which server(s), what position, and for how long.*\n\n"
            f"**Question 5**\n"
            f"What kinds of building experience do you have? What kinds of things have you built or helped out with, and would you consider yourself a beginner, intermediate, or advanced builder?\n\n"
            f"**Question 6**\n"
            f"What are your strengths and weaknesses in building? What areas do you prefer and what areas do you dislike?\n\n"
            f"**Question 7**\n"
            f"Do you work better in a team or solo (or either)?\n\n"
            f"**Question 8**\n"
            f"How familiar are you with building plugins such as WorldEdit and VoxelSniper?\n\n"
            f"**Question 9**\n"
            f"How many kangaroos could you fight off and why?\n\n"
            f"**Question 10**\n"
            f'In a follow-up message, please upload at least 3 screenshots (no shaders, default resourcepack!) of your builds, and simply say "images" as your answer to this question.' 
            f"If you have more builds to showcase, you may make a portfolio on https://imgur.com/ and paste the link as your answer.\n\n"                              
            f"**Head Builders**\n"
            f"{WeirdoFish_user.mention}"
            f"{Hapu_user.mention}",
            color=discord.colour.Color.green(),
        )
        embed.set_footer(text='● Parcade Staff Management ●')
        await interaction.channel.send(embed=embed)
        await interaction.message.delete()            
            
    @discord.ui.button(style=ButtonStyle.blurple, label="GUIDE", emoji="⚖", custom_id="guide_apply")
    async def guide_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        Cerdax_user = bot.get_user(int("ID"))
        embed=discord.Embed(
            title="⟪ GUIDE APPLICATION ⟫",
            description=
            f"On the Parcade Network, a Guide is one step down from a mod, who moderates "
            f"chat both in-game and in the discord, as well as answers questions and assists " 
            f"players no matter the issue. They are mainly there to maintain peace and provide "
            f"support to players, helping in which ever way they can.\n\n"
            f"**Tasks of a Guide**\n"
            f"- Warn/Mute people in-game\n"
            f"- Warn/Mute people in the Discord\n"
            f"- Let mods know about hackers (reported by players)\n"
            f"- Reply to tickets\n"
            f"- Answer/address any player questions or concerns\n\n"
            f"---------------------------------------------------------------\n"
            f"Please respond in the following format:\n\n"
            f"Question 1: (Your answer)\n"
            f"Question 2: (Your answer)\n"
            f"...\n"
            f"---------------------------------------------------------------\n\n"
            f"**Question 1**\n"
            f"What is your Minecraft username?\n\n"
            f"**Question 2**\n"
            f"How old are you?\n"
            f"*(be honest, we will find out if you're not)\n\n"
            f"**Question 3**\n"
            f"Have you been punished on the Parcade Network before?\n"
            f'Please tell us what the punishment(s) was, or reply "none"\n\n'
            f"**Question 4**\n"
            f"Have you been staff on any other servers?\n"
            f"*If so, tell us which server(s), what position, and for how long.*\n\n"
            f"**Question 5**\n"
            f"If a player asks you a question, and you do not know the answer, how will you respond, or what will you do?\n\n"
            f"**Question 6**\n"
            f"Suppose three players are arguing about a world record, and it is getting out of hand. How will you respond to the situation?\n\n"
            f"**Question 7**\n"
            f"If you are on the server and witness a hacker stealing many world records, what would you do?\n\n"
            f"**Question 8**\n"
            f"Let's say a player starts spamming in #general with racist remarks, how would you maintain control and punish them?\n\n"
            f"**Question 9**\n"
            f"How many pillows do you sleep with?\n\n"
            f"**Question 10**\n"
            f"Do you have a working microphone for a follow-up interview that will test your knowledge about the Parcade?\n"
            f"*Exceptions can be made, but voice chat prefered.*\n\n"                             
            f"**Head of Staff (Recruitment / Mentoring)**\n"
            f"{Cerdax_user.mention}",
        color=discord.colour.Color.brand_green(),
        )
        embed.set_footer(text='● Parcade Staff Management ●')
        await interaction.channel.send(embed=embed)
        await interaction.message.delete()
        
    @discord.ui.button(style=ButtonStyle.danger, label="DEV", emoji="🤖", custom_id="dev_apply")
    async def developer_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        Timmetatsch_user = bot.get_user(int("ID"))
        embed=discord.Embed(
            title="Developer",
            description=
                f"As a developer you will help us to create new games and maintain our server. "
                f"You may also help or focus entirely on working on our website. As a game developer you will be expected " 
                f"to have advanced knowledge of the Java language and a decent understanding of spigot. "
                f"You should also have an intuitive understanding for how parkour-related mechanics work in "
                f"Minecraft. Basic knowledge in SQL would be nice but isn't required. \n\n"
                f"Since we will be working in a team, you must be able to write clean and maintainable code. \n\n"
                f"We have certain in-house APIs that we use and will happily assist you in learning how to use them. \n\n"
                f"By joining the dev team you will be able to change existing and add entirely new features and fundamentally "
                f"shape the future of our server in the process.\n\n"
                f"**Tasks of a Developer**\n"
                f"- create new plugins for new game modes \n"
                f"- maintain and improve existing plugins \n"
                f"- extend our APIs \n"
                f"- maintain and improve our website \n\n"
                f"---------------------------------------------------------------\n"
                f"Please respond in the following format:\n\n"
                f"Question 1: (Your answer)\n"
                f"Question 2: (Your answer)\n"
                f"...\n"
                f"---------------------------------------------------------------\n\n"
                f"**Question 1**\n"
                f"What is your Minecraft username?\n\n"
                f"**Question 2**\n"
                f"How old are you?\n"
                f"*(be honest, we will find out if you're not)\n\n"
                f"**Question 3**\n"
                f"Have you been punished on the Parcade Network before?\n"
                f'Please tell us what the punishment(s) was, or reply "none"\n\n'
                f"**Question 4**\n"
                f"Have you been staff on any other servers?\n"
                f"*If so, tell us which server(s), what position, and for how long.*\n\n"
                f"**Question 5**\n"
                f"What was the most challenging coding project that you have ever worked on (not necessarily Minecraft related) and what made it challenging?\n\n"
                f"**Question 6**\n"
                f"How much experience do you have with writing plugins for spigot? (ignore for web dev application)\n\n"
                f"**Question 7**\n"
                f"What projects would you like to work on or contribute to on Parcade?\n\n"
                f"**Question 8**\n"
                f"Which part of being a developer would excite you the most?\n\n"
                f"**Question 9**\n"
                f"Do you prefer sparkling or still water?\n\n"
                f"**Question 10**\n"
                f"Please provide a link (or file) to a plugin/web application that you have written or contributed to.\n\n"                              
                f"**Head of Development**\n"
                f"{Timmetatsch_user.mention}",
            color=discord.colour.Color.orange(),
        )
        embed.set_footer(text='● Parcade Staff Management ●')
        await interaction.channel.send(embed=embed)
        await interaction.message.delete()
    @discord.ui.button(style=ButtonStyle.grey, label="CLOSE", emoji="❌", custom_id="close_ticket")
    async def close_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.message.delete()
        category = await bot.fetch_channel(CLOSED_CATEGORY_ID)
        await interaction.channel.edit(category=category)
        embed2 = discord.Embed(
            title="⟪ CLOSED TICKET ⟫",
            description=
            f"Your ticket got closed. This likely happened because of the following reasons: \n" 
            f"- you decided to close your ticket \n"
            f"- the topic has been resolved \n"
            f"- there hasn't been a reply from you in some time\n\n"
            f'If you feel like your case is not resolved, please click on the "Open Again" button. \n\n'
            f"Do not hesistate to reach out to us again."
            f"\n"
            f"Thank you for reaching out to our staff team!",
            color=discord.colour.Color.dark_grey(),
        )
        embed2.set_footer(text='● Parcade Ticket System ●')
        view = OpenAgain()
        close_message = await interaction.response.send_message(embed=embed2, view=view)
        view.message = close_message
        
class Rule_Buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(1,2, commands.BucketType.member)
    @discord.ui.button(style=ButtonStyle.danger, label="REPORT", emoji="🚨", custom_id="report")
    async def report_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        interaction.message.author = interaction.user
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()
        if retry:
            return await interaction.response.send_message(f"Slow down! Try again in {round(retry, 1)} seconds.", ephemeral=True)
        guild = bot.get_guild(GUILD_ID)
        category = bot.get_channel(SUPPORT_CATEGORY_ID)
        topic = "Report"
        guide_role: discord.Role = guild.get_role(GUIDE_ID)
        mod_role: discord.Role = guild.get_role(MODERATOR_ID)
        
        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True),
        mod_role: discord.PermissionOverwrite(view_channel=True),
        mod_role: discord.PermissionOverwrite(read_messages=True),
        guide_role: discord.PermissionOverwrite(view_channel=True),
        guide_role: discord.PermissionOverwrite(read_messages=True),
        }
        
        # CHECK IF USER CREATED A TICKET
        last_ticket_date = get_last_ticket(interaction.user.id)
        if last_ticket_date != None:
            time_since_last_ticket = int(datetime.now().timestamp()) - last_ticket_date
            if time_since_last_ticket < 30:
                embed = discord.Embed(
                    title="Please be patient.",
                    description="Please wait a bit before opening a new ticket",
                    color=discord.colour.Color.red(),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                print("Last Ticket longer than 30 seconds ago.")
        else:
            print("Never had a ticket before.")
        
        await interaction.response.defer()
        ticket_number = set_ticket_number(interaction.user)
            

        # CREATING THE CHANNEL IN SUPPORT AREA
        ticket_channel = await category.create_text_channel(
            f"ticket-{topic}-{ticket_number}",
            topic=f"Ticket from {interaction.user} Topic: {topic} Client-ID: {interaction.user.id} ",
            overwrites=overwrites,
        )
        
        # DATABASE ENTRY OF THE TICKET CREATION
        playerdb = connect()
        playerdb.commit()
        cursor = playerdb.cursor()
        now = int(datetime.now().timestamp())
        
        sql = (
            "INSERT INTO discord_tickets (ticket_number, ticket_status, ticket_date, channel_id, user_id, ticket_topic) VALUES (%s, %s, %s, %s, %s, %s)"
        )
        val = (ticket_number, 1, now, ticket_channel.id, interaction.user.id, topic)
        cursor.execute(sql, val)

        playerdb.commit()
        playerdb.close()
        channel = ticket_channel
        
        # CHANNEL CREATION EMBED
        embed = discord.Embed(
        title="Ticket started",
        description=f'Your ticket was created, please look into the "Support Channel" section below.',
        color=discord.colour.Color.green(),
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        await report_message(ticket_channel)
        
    @discord.ui.button(style=ButtonStyle.blurple, label="APPEAL", emoji="🔒", custom_id="appeal")
    async def appeal_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.defer()
        guild = bot.get_guild(GUILD_ID)
        category = bot.get_channel(SUPPORT_CATEGORY_ID)
        topic = "Appeal"
        mod_role: discord.Role = guild.get_role(MODERATOR_ID)
        
        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True),
        mod_role: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
        }
        
        # CHECK IF USER CREATED A TICKET
        last_ticket_date = get_last_ticket(interaction.user.id)
        if last_ticket_date != None:
            time_since_last_ticket = int(datetime.now().timestamp()) - last_ticket_date
            if time_since_last_ticket < 30:
                embed = discord.Embed(
                    title="Please be patient.",
                    description="Please wait a bit before opening a new ticket",
                    color=discord.colour.Color.red(),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                print("Last Ticket longer than 30 seconds ago.")
        else:
            print("Never had a ticket before.")
            
        ticket_number = set_ticket_number(interaction.user)
            
        # CREATING THE CHANNEL IN SUPPORT AREA
        ticket_channel = await category.create_text_channel(
            f"ticket-{topic}-{ticket_number}",
            topic=f"Ticket from {interaction.user} Topic: {topic} Client-ID: {interaction.user.id} ",
            overwrites=overwrites,
        )
        
        # DATABASE ENTRY OF THE TICKET CREATION
        playerdb = connect()
        playerdb.commit()
        cursor = playerdb.cursor()
        now = int(datetime.now().timestamp())

        sql = (
            "INSERT INTO discord_tickets (ticket_number, ticket_status, ticket_date, channel_id, user_id, ticket_topic) VALUES (%s, %s, %s, %s, %s, %s)"
        )
        val = (ticket_number, 1, now, ticket_channel.id, interaction.user.id, topic)
        cursor.execute(sql, val)

        playerdb.commit()
        playerdb.close()
        
        # CHANNEL CREATION EMBED
        embed = discord.Embed(
            title="Ticket started",
            description=f'Your ticket was created, please look into the "Support Channel" section below.',
            color=discord.colour.Color.green(),
        )

        #SEND BOTH EMBED IN TICKET OPEN AND NEW CHANNEL
        await interaction.followup.send(embed=embed, ephemeral=True)
        await appeal_message(ticket_channel)
        
    @discord.ui.button(style=ButtonStyle.green, label="APPLY", emoji="✉️", custom_id="apply")
    async def apply_callback (self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.defer()
        guild = bot.get_guild(GUILD_ID)
        category = bot.get_channel(SUPPORT_CATEGORY_ID)
        topic = "Apply"
        mod_role: discord.Role = guild.get_role(MODERATOR_ID)
        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True),
        mod_role: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
        }
        # CHECK IF USER CREATED A TICKET
        last_ticket_date = get_last_ticket(interaction.user.id)
        if last_ticket_date != None:
            time_since_last_ticket = int(datetime.now().timestamp()) - last_ticket_date
            if time_since_last_ticket < 30:
                embed = discord.Embed(
                    title="Please be patient.",
                    description="Please wait a bit before opening a new ticket",
                    color=discord.colour.Color.red(),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                print("Last Ticket longer than 30 seconds ago.")
        else:
            print("Never had a ticket before.")
            
        ticket_number = set_ticket_number(interaction.user)
        
        # CREATING THE CHANNEL IN SUPPORT AREA
        ticket_channel = await category.create_text_channel(
            f"ticket-{topic}-{ticket_number}",
            topic=f"Ticket from {interaction.user} Topic: {topic} Client-ID: {interaction.user.id} ",
            overwrites=overwrites,
        )
        

        # DATABASE ENTRY OF THE TICKET CREATION
        playerdb = connect()
        playerdb.commit()
        cursor = playerdb.cursor()
        now = int(datetime.now().timestamp())

        sql = (
            "INSERT INTO discord_tickets (ticket_number, ticket_status, ticket_date, channel_id, user_id, ticket_topic) VALUES (%s, %s, %s, %s, %s, %s)"
        )
        val = (ticket_number, 1, now, ticket_channel.id, interaction.user.id, topic)
        cursor.execute(sql, val)

        playerdb.commit()
        playerdb.close()
        
        # CHANNEL CREATION EMBED
        embed = discord.Embed(
            title="Ticket started",
            description=f'Your ticket was created, please look into the "Support Channel" section below.',
            color=discord.colour.Color.green(),
        )

        #SEND BOTH EMBED IN TICKET OPEN AND NEW CHANNEL
        await interaction.followup.send(embed=embed, ephemeral=True)
        await apply_message(ticket_channel)
        
    @discord.ui.button(style=ButtonStyle.gray, label="OTHER", custom_id="other")
    async def other_callback (self, interaction: discord.Interaction, Button: discord.ui.Button): 
        await interaction.response.defer()
        guild = bot.get_guild(GUILD_ID)
        category = bot.get_channel(SUPPORT_CATEGORY_ID)
        topic = "Other"
        mod_role: discord.Role = guild.get_role(MODERATOR_ID)
        guide_role: discord.Role = guild.get_role(GUIDE_ID)
        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True),
        mod_role: discord.PermissionOverwrite(send_messages=True),
        guide_role: discord.PermissionOverwrite(send_messages=True),
        }   
        
        
        # CHECK IF USER CREATED A TICKET
        last_ticket_date = get_last_ticket(interaction.user.id)
        if last_ticket_date != None:
            time_since_last_ticket = int(datetime.now().timestamp()) - last_ticket_date
            if time_since_last_ticket < 30:
                embed = discord.Embed(
                    title="Please be patient.",
                    description="Please wait a bit before opening a new ticket",
                    color=discord.colour.Color.red(),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                print("Last Ticket longer than 30 seconds ago.")
        else:
            print("Never had a ticket before.")
            
        ticket_number = set_ticket_number(interaction.user)
        
        # CREATING THE CHANNEL IN SUPPORT AREA
        ticket_channel = await category.create_text_channel(
            f"ticket-{topic}-{ticket_number}",
            topic=f"Ticket from {interaction.user} Topic: {topic} Client-ID: {interaction.user.id} ",
            overwrites=overwrites,
        )

        # DATABASE ENTRY OF THE TICKET CREATION
        playerdb = connect()
        playerdb.commit()
        cursor = playerdb.cursor()
        now = int(datetime.now().timestamp())

        sql = (
            "INSERT INTO discord_tickets (ticket_number, ticket_status, ticket_date, channel_id, user_id, ticket_topic) VALUES (%s, %s, %s, %s, %s, %s)"
        )
        val = (ticket_number, 1, now, ticket_channel.id, interaction.user.id, topic)
        cursor.execute(sql, val)

        playerdb.commit()
        playerdb.close()
        
        # CHANNEL CREATION EMBED
        embed = discord.Embed(
            title="Ticket started",
            description=f'Your ticket was created, please look into the "Support Channel" section below.',
            color=discord.colour.Color.green(),
        )

        #SEND BOTH EMBED IN TICKET OPEN AND NEW CHANNEL
        await interaction.followup.send(embed=embed, ephemeral=True)
        await other_message(ticket_channel)
        
@bot.command()        
async def ticketbuttons(ctx):
    PERMISSIONS = "ticket.commands.buttons"
    has_perms = check_perms(ctx.author.id, PERMISSIONS)
    if has_perms == False:
        print("NO PERMS")
        return
    whatodo = discord.Embed(
            title="⟪ Parcade Ticket System ⟫",
            description="Creating a ticket is a way to bring attention to an issue "
            f"or topic you need assistance with. Whether dealing with a bug, someone breaking the rules, or a "
            f"question, our staff is here to help you work it out.\n\n"
            f"To open a ticket, please click the button below this message that best fits your case.\n\n"
            f"🚨 **Reports**\n"
            f"You can report bugs, players, exploits and more for our team to help out as quickly as possible. "
            f"Talk directly to our staff and give them all the details you have. "
            f"For the report of staff members, please talk to an Owner directly.\n\n"
            f"🔒 **Appeals**\n"
            f"If you believe that a punishment you received on our Minecraft Network or on Discord was unjustified, "
            f"you can appeal it here. Please provide detailed information and evidence to support your appeal, " 
            f"so that our staff can review it promptly. Please note that our staff's decisions are final, but we "
            f"strive to maintain a fair and safe environment for all players.\n\n"
            f"✉️ **Applications**\n"
            f"Apply to join our team and help out the Parcade Network! We are searching for motivated players " 
            f"for guide, developer, and builder. Your contributions will impact the success of Parcade and "
            f"make it a better place. Whether you prefer to actively help with server development or passively assist "
            f"by suggesting new ideas and help testing, your participation is greatly appreciated. Apply now and "
            f"be part of shaping the future of our community!\n\n"
            f"📝 **Anything else**\n"
            f"Additionally to the other topics, you can open a ticket for **Map Submissions**, **Ideas**, **Complaints** " 
            f'or **General Questions** that you want to have discussed in private with our staff team. '
            f'However, please do not waste our time and resources with silly, minimal topics or just to have a conversation. '
            f"For those things you can use the default channels in this discord. This is not the right place for **Partnership Requests**.\n",
            color=0xFFFFFF,
    )

    await ctx.send(embed=whatodo, view=Rule_Buttons())

async def report_message(ticket_channel):
    # EMBED REPORT CHANNEL
    info_channel = bot.get_channel(INFO_CHANNEL_ID)
    embed2 = discord.Embed(
        title="⟪ Report ⟫",
        description=
        f"You chose to open a ticket for a report. In this case, there are two options, which are stated below. "
        f"Please read carefully and then continue with posting your report. \n\n" 
        f"**Player Reports**\n"
        f"The first option is to report a player for breaking the rules. If a player broke the rules "
        f"in the {info_channel.mention} channel, it is the right decision to report him here. Please make sure to be as " 
        f"detailed as possible about your report. If you have any evidence, like screenshots, videos or anything else "
        f"please attach it to the report.\n\n"
        f"**Bug Reports**\n"
        f"The second option is to report a bug you have found on our network. If there is anything you have "
        f"found which is not working as intended, you figured out an exploit on a parkour map or you are stuck "
        f"please let us know. There is nothing wrong with reporting an issue which you are not sure about. "
        f"Please provide a screenshot or video of the problem into this channel or send us a link. "
        f"(e.g. Youtube video which is unlisted)\n\n"
        f"**BE AWARE**\n"
        f"After you posted your report, please be patient as we process your concern and get back to you as "
        f"soon as we can! Please don't ping anyone, we will talk to you as soon as we can.\n\n"
        f"**OPENED THE WRONG TICKET?**\n"
        f'Do not worry, you can close the ticket with the "Close" button below',
        color=discord.colour.Color.red(),
    )
    embed2.set_footer(text='● Parcade Report System ●')
    response = embed2
    #SEND BOTH EMBED IN TICKET OPEN AND NEW CHANNEL
    view = Close()
    message = await ticket_channel.send(embed=response, view=view)
    view.message = message
    
async def appeal_message(ticket_channel):
    Bwen391_user = bot.get_user(int(173779204666556417))
    # EMBED APPEAL CHANNEL
    embed2 = discord.Embed(
        title="⟪ Appeal ⟫",
        description=
        f"You chose to open a ticket for a punishment appeal. Please carefully read through the questions stated below and answer them all as detailed as you can. \n\n" 
        f"**Questions**\n"
        f"1. Why were you punished? (Punishment Message) \n"
        f"2. What is your in-game name? \n"
        f"3. Do you think you were rightfully punished? (Yes / No) \n"
        f"4. Why should we revoke your punishment ? (Reason) \n"
        f"5. If the punishment is not older than a year, do you have evidence for not being guilty ? (optional - Yes / No) \n\n"
        f"**Head of Rules**\n"
        f"{Bwen391_user.mention}\n\n"
        f"**OPENED THE WRONG TICKET?**\n"
        f'Do not worry, you can close the ticket with the "Close" button below',
        color=discord.colour.Color.blue(),
    )
    embed2.set_footer(text='● Parcade Punishment Appeals ●')
    response = embed2
    view = Close()
    message = await ticket_channel.send(embed=response, view=view)
    view.message = message
    
async def apply_message(ticket_channel):
    embed2 = discord.Embed(
        title="⟪ Application ⟫",
        description=
        f"You chose to open a ticket for an application. In this case, there is three options, which are stated below. \n\n"
        f"Please read carefully and then choose the position you want to apply to.\n\n" 
        f"⛏ **Builder**\n"
        f"When you join the Parcade Build Team, you can build maps, lobbies and more together with other builders!\n\n"
        f"**Tasks of a Builder**\n"
        f"- Build various types of maps using plugins such as WorldEdit and VoxelSniper alone or with other people \n"
        f"- Build larger maps with the team while getting along with everyone \n"
        f"- Review other builders' maps and help improve them \n"
        f"- Test maps before release to make sure they are built correctly \n"
        f"- Help out with the building side of various projects led by higher staff \n\n"
        f"⚖ **Guide**\n"
        f"When you join the Parcade Staff Team as a Guide, you can moderate the chat and help out players!\n\n"
        f"**Tasks of a Guide**?\n"
        f"- Warn/Mute people in-game\n"
        f"- Warn/Mute people in the Discord\n"
        f"- Let mods know about hackers (reported by players)\n"
        f"- Reply to tickets\n"
        f"- Answer/address any player questions or concerns\n"
        f"🤖 **Developer**\n"
        f"When you join the Parcade Development Team, you will actively help to develop the servers conception and functionality!\n\n"
        f"**Tasks of a Developer**\n"
        f"- create new plugins for new game modes \n"
        f"- maintain and improve existing plugins\n"
        f"- extend our APIs \n"
        f"- maintain and improve our website \n\n"
        f"**OPENED THE WRONG TICKET?**\n"
        f'Do not worry, you can close the ticket with the "Close" button below',
        color=discord.colour.Color.purple(),
    )
    embed2.set_footer(text='● Parcade Staff Management ●')
    response = embed2
    view = Application_Buttons()
    message = await ticket_channel.send(embed=response, view=view)
    view.message = message    

async def other_message(ticket_channel):
    # EMBED APPLY CHANNEL
    embed2 = discord.Embed(
        title="⟪ Other Issue ⟫",
        description=
        f"You opened a ticket for something that was not listed, we'd love to help you out "
        f"but make sure it is a relevant and important issue. Please state what we can assist " 
        f"you with - **in detail** - and be patient as we process your concern!\n\n"
        f"As you wait, please be patient and make sure to be nice to our staff team.\n\n"
        f"**OPENED THE WRONG TICKET?**\n"
        f'Do not worry, you can close the ticket with the "Close" button below',
        color=discord.colour.Color.dark_grey(),
    )
    embed2.set_footer(text='● Parcade Ticket System ●')
    response = embed2
    view = Close()
    message = await ticket_channel.send(embed=response, view=view)
    view.message = message   
    
        

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send(
            "Couldn't find the command. Type `pchelp` for a list of commands."
        )


@bot.command()
async def close(ctx, point=None):
    PERMISSIONS = "ticket.channel.archive"
    print("hi")
    has_perms = check_perms(ctx.author.id, PERMISSIONS)
    if has_perms == False:
        print("NO PERMS")
        return
    
    # VARIABLES
    admin_channl = bot.get_channel(ADMIN_CHANNEL_LOG)
    
    channel = ctx.channel
    attach_c = 0
    
    if "ticket" in ctx.channel.name:
        channel_id = ctx.channel.id
        
        if channel.category_id == SUPPORT_CATEGORY_ID:
            PERMISSIONS = "ticket.channel.archive.open"
            has_perms = check_perms(ctx.author.id, PERMISSIONS)
            
            if has_perms == False:
                print("NO PERMS")
                return
        
        # DATABASE CLOSE UPDATE
        playerdb = connect()
        cursor = playerdb.cursor()
        sql = "UPDATE discord_tickets SET ticket_status = 0 WHERE channel_id = %s"
        val = (channel_id,)
        cursor.execute(sql, val)
        playerdb.commit()
        
        
        # RECEIVE TICKET DATA FOR ARCHIVE 
        playerdb.commit()
        cursor = playerdb.cursor()
        sql = "SELECT ticket_date, user_id, ticket_topic FROM discord_tickets WHERE channel_id = %s"
        val = (channel_id,)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        playerdb.close()
        
        ticket_user_raw = bot.get_user(int(result[0][1]))
        ticket_user_id = str(ticket_user_raw.id)
        ticket_user = ticket_user_raw.name
        ticket_date_raw = datetime.fromtimestamp(int(result[0][0]))
        ticket_date = ticket_date_raw.strftime("%d/%B/%Y, %H:%M:%S")
        ticket_topic = result[0][2]
        command_author = str(ctx.author.id)
        

        # REPORT SCORE IF REAL REPORT WAS MADE
        if point == "+" and ticket_topic == "Report":
            print("Argument: + Topic: Report")
            # CHECK IF PLAYER IS IN STATS TABLE
            playerdb = connect()
            cursor = playerdb.cursor()
            sql = "INSERT INTO discord_stats (discord_id, report_score, mod_score, creative_score, bot_score) VALUES (%s, 1, 0, 0, 0) ON DUPLICATE KEY UPDATE report_score = report_score+1"
            val = (ticket_user_id,)
            cursor.execute(sql, val)
            playerdb.commit()
            playerdb.close()
            # MOD SCORE FOR TICKET 

        playerdb = connect()
        cursor = playerdb.cursor()
        sql = "INSERT INTO discord_stats (discord_id, report_score, mod_score, creative_score, bot_score) VALUES (%s, 0, 1, 0, 0) ON DUPLICATE KEY UPDATE mod_score = mod_score+1"
        val = (command_author,)
        cursor.execute(sql, val)
        playerdb.commit()
        playerdb.close()

        filename = f'{channel.id}{ticket_user_id}'
        
        embed = discord.Embed(
            title="Archiving Messages",
            description="Hold on, while we are archiving the messages of this channel. Depending on the length of the ticket, this can take a while.",
            color=0xFC9233,
        )
        
        await ctx.channel.send(embed=embed)
        
        
        with open(f'/srv/bot/archive/{filename}.txt', 'w', encoding="utf-8") as f:
            f.write(f'Ticket from: {ticket_user} opened: {ticket_date} topic: "{ticket_topic}"\n')
        
            async for message in channel.history(limit=None):
                f.write(f'[{message.created_at.strftime("%d/%m/%Y, %H:%M:%S")}] {message.author.name}: {message.clean_content}\n')
                if len(message.attachments) > 0: 
                    
                    i = 0
                    while(i < len(message.attachments)):
                        print(message.attachments)
                        if message.attachments[i].url.endswith(("png", "jpg", "jpeg")):
                            print("pic")
                            try:
                                url = message.attachments[i].url
                                if url[0:26] == "https://cdn.discordapp.com":
                                    r = requests.get(url, stream=True)
                                    imageName = str(filename) + str(attach_c) + '.jpg'
                                    attach_c=attach_c+1
                                    with open(f'/srv/bot/archive/{imageName}', 'wb') as out_file:
                                        print("Saving image: " + imageName)
                                        shutil.copyfileobj(r.raw, out_file)
                            except IndexError:
                                print("Error")
                        if message.attachments[i].url.endswith(("mp4")):
                            try:
                                url = message.attachments[i].url 
                                if url[0:26] == "https://cdn.discordapp.com":
                                    r = requests.get(url, stream=True)
                                    imageName = str(filename) + str(attach_c) + '.mp4'
                                    attach_c=attach_c+1
                                    with open(f'/srv/bot/archive/{imageName}', 'wb') as out_file:
                                        print("Saving video: " + imageName)
                                        shutil.copyfileobj(r.raw, out_file)
                            except IndexError:
                                print("Error")
                        if message.attachments[i].url.endswith(("mp3")):
                            try:
                                url = message.attachments[i].url 
                                if url[0:26] == "https://cdn.discordapp.com":
                                    r = requests.get(url, stream=True)
                                    imageName = str(filename) + str(attach_c) + '.mp3'
                                    attach_c=attach_c+1
                                    with open(f'/srv/bot/archive/{imageName}', 'wb') as out_file:
                                        print("Saving audio: " + imageName)
                                        shutil.copyfileobj(r.raw, out_file)
                            except IndexError:
                                print("Error")
                        if message.attachments[i].url.endswith(("gif")):
                            try:
                                url = message.attachments[i].url 
                                if url[0:26] == "https://cdn.discordapp.com":
                                    r = requests.get(url, stream=True)
                                    imageName = str(filename) + str(attach_c) + '.gif'
                                    attach_c=attach_c+1
                                    with open(f'/srv/bot/archive/{imageName}', 'wb') as out_file:
                                        print("Saving gif: " + imageName)
                                        shutil.copyfileobj(r.raw, out_file)
                            except IndexError:
                                print("Error")
                        if message.attachments[i].url.endswith(("doc", "docx", "pdf")):
                            try:
                                url = message.attachments[i].url 
                                if url[0:26] == "https://cdn.discordapp.com":
                                    r = requests.get(url, stream=True)
                                    imageName = str(filename) + str(attach_c) + '.docx'
                                    attach_c=attach_c+1
                                    with open(f'/srv/bot/archive/{imageName}', 'wb') as out_file:
                                        print("Saving document: " + imageName)
                                        shutil.copyfileobj(r.raw, out_file)
                            except IndexError:
                                print("Error")
                        if message.attachments[i].url.endswith(("txt")):
                            try:
                                url = message.attachments[i].url 
                                if url[0:26] == "https://cdn.discordapp.com":
                                    r = requests.get(url, stream=True)
                                    imageName = str(filename) + str(attach_c) + '.txt'
                                    attach_c=attach_c+1
                                    with open(f'/srv/bot/archive/{imageName}', 'wb') as out_file:
                                        print("Saving txt: " + imageName)
                                        shutil.copyfileobj(r.raw, out_file)
                            except IndexError:
                                print("Error")
                        if message.attachments[i].url.endswith(("zip")):
                            try:
                                url = message.attachments[i].url 
                                if url[0:26] == "https://cdn.discordapp.com":
                                    r = requests.get(url, stream=True)
                                    imageName = str(filename) + str(attach_c) + '.zip'
                                    attach_c=attach_c+1
                                    with open(f'/srv/bot/archive/{imageName}', 'wb') as out_file:
                                        print("Saving zip: " + imageName)
                                        shutil.copyfileobj(r.raw, out_file)
                            except IndexError:
                                print("Error")
                        if message.attachments[i].url.endswith(("jar")):
                            try:
                                url = message.attachments[i].url 
                                if url[0:26] == "https://cdn.discordapp.com":
                                    r = requests.get(url, stream=True)
                                    imageName = str(filename) + str(attach_c) + '.jar'
                                    attach_c=attach_c+1
                                    with open(f'/srv/bot/archive/{imageName}', 'wb') as out_file:
                                        print("Saving jar: " + imageName)
                                        shutil.copyfileobj(r.raw, out_file)
                            except IndexError:
                                print("Error")
                        i=i+1       
                if "tenor.com" in message.content:
                    match = re.search(r'https?://[^\s]+', message.content)
                    if match:
                        link = match.group(0)  
                        await admin_channl.send("Here is a gif from " + str(ctx.channel.name) + "! Enjoy. " + str(link))  
                        await asyncio.sleep(2)
                if "youtu.be" in message.content:
                    match = re.search(r'https?://[^\s]+', message.content)
                    if match:
                        link = match.group(0)  
                        await admin_channl.send("Here is a Youtube from " + str(ctx.channel.name) + "! Please download and archive it: " + str(link))  
                        await asyncio.sleep(2)
                if "youtube.com" in message.content:            
                    match = re.search(r'https?://[^\s]+', message.content)
                    if match:
                        link = match.group(0)  
                        await admin_channl.send("Here is a Youtube from " + str(ctx.channel.name) + "! Please download and archive it: " + str(link))  
                        await asyncio.sleep(2)
                        
                
        await admin_channl.send("Messaged Saved (Found " + str(attach_c) + " Files)", file=discord.File(f'/srv/bot/archive/{filename}.txt'))
        
        embed = discord.Embed(
            title="Message Archiving Completed",
            description="Thanks for waiting.",
            color=0xFC9233,
        )   
        await ctx.channel.send(embed=embed)
        await asyncio.sleep(2)
        
        embed = discord.Embed(
            title="Ticket Solved",
            description="This ticket closes in 5 seconds..",
            color=0xFC9233,
        )
        await ctx.channel.send(embed=embed)
        await asyncio.sleep(5)
        await ctx.channel.delete()
        
        
        
@bot.event
async def on_guild_channel_delete(channel):
    print(channel)
    

@bot.command()
async def restart(ctx):
    if ctx.channel.id == 1061650280850137138:
        if ctx.author.id == 173779204666556417 or ctx.author.id == 280654220254773248 or ctx.author.id == 191474138450362369 or ctx.author.id == 356257712750985218:
            await ctx.send("Restarting the bot...")
            os.execv(sys.executable, ["python3"] + sys.argv)
        else:
            await ctx.send("You do not have permission to use this command.")
        
    


bot.run('ID')