import discord
import subprocess
import requests
import random
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
#from datetime
from datetime import datetime
import sys
import asyncio
import json
import aspen
from aspen import moderation, messaging, logevents, extension
import importlib
from addict import Dict
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import aioconsole
startTime = datetime.now()
softmute = []
sniper = {}
f = open("settings.json")
Intents = discord.Intents.default()
Intents.members = True
client = commands.AutoShardedBot(command_prefix="$", intents=Intents, shard_count=3, shard_ids=[0, 1, 2])
slash = SlashCommand(client, sync_commands=True)
settings = {}
try:
    settings = Dict(json.load(f))
    f.close()
except:
    print("An error occurred while loading settings")

f = open("banned_words.json")
botConfig = Dict(json.load(open("config.json")))
chatFilter = Dict(json.load(f))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="APIs"))
    client.loop.create_task(backgroundTask())

@client.event
async def on_member_join(member):
    if member.bot:
        return
    if member.guild.id == 806151212814565386:
        channel = client.get_channel(825096484180983868)
        await channel.send(member.mention+" Welcome to Subway! You can get roles from <#806156381933273108>, <#819280783067316224>, and <#823398921581101056>")
    return
@client.event
async def on_message_edit(before, after):
    if after.author == client.user:
        return
    if "discord.gg/" in after.content:
        if not after.author.guild_permissions.manage_messages:
            await after.delete()
    if after.author.id == 750835145556230206:
        if after.content == "This is a legal message to confirm to the public that may find my previous messages that may contain the words “simp”, or may indicate that I could be a simp, that I am not in fact a simp. Everything I say is for jokes and jokes only, therefore I am not a simp in any way, shape or form. Also to note, I am presently not dating anyone online. Anything I say that could possibly indicate that I am dating someone presently is to be automatically invalidated, and is used for jokes and jokes only.":
            await after.delete()
    for key in chatFilter['bannedWords']:
        text = after.content.lower()
        if key in text.split() and after.author.id != 193112730943750144:
            await after.delete()
            embed = discord.Embed(title="Global Filter", description="Banned word triggered by `Wildcard`", colour=discord.Colour.from_rgb(255, 0, 242))
            embed.add_field(name="Banned Word", value=key)
            embed.add_field(name="Full Message", value=after.content, inline=False)
            embed.set_author(name=after.author.name+'#'+after.author.discriminator, icon_url=after.author.avatar_url)
            channel = client.get_channel(int(settings[str(after.guild.id)]["Channels"]["Logging"]))
            await channel.send(embed=embed)
@client.event
async def on_message_delete(message):
    global sniper
    if message.content.startswith("""Tristin: You wouldn't believe what happened to me today. My furry girlfriend today didn't want to have sex with me...tch. I growled at her and showed her my sharp fans which, of course, put her in heat. She tried to run away from me but her pussy was so wet it was leaving a trail behind her, I could sniff her out. I heard the sound of her fat ass clapping together as she ran and I couldn't help but have a raging boner at the thought of me inside her wet pussy. It turns out, she was cheating on me with some prick named Alec. I growled at Alec, turned him into a puppy. Then I went to my furry girlfriend and said, "Sorry, I don't date hoes." then I slapped her with my raging boner and she flew into a wall and fucking died. Yeah so, I'm single now."""):
        msg = await message.channel.send(message.content)
        await msg.pin()
        #await msg.pin()
    if message.author.bot:
        return
    if message.author.id == 219838416878174209:
        return
    await aspen.logevents.deleteLog(client, message)
    if str(message.channel.id) not in sniper:
        sniper.setdefault(str(message.channel.id),[])
    key = str(message.channel.id)
    value = message
    sniper[key] = [value] if key not in sniper else sniper[key] + [value]
    if len(sniper[key]) > 5:
        sniper[key].pop(0)


@client.event
async def on_message(message):
    global softmute
    global settings
    global chatFilter
    global sniper

    if message.content.startswith('$reload'):
        if message.author.id != 193112730943750144:
            return
        op = message.content.lower().split()
        if op[1] == 'logger':
            importlib.reload(aspen.logevents)
            await message.channel.send("Reloading Module: **Logger**")
        if op[1] == 'moderation':
            importlib.reload(aspen.moderation)
            await message.channel.send("Reloading Module: **Moderation**")
        if op[1] == 'messaging':
            importlib.reload(aspen.messaging)
            await message.channel.send("Reloading Module: **Messaging**")
        if op[1] == 'utils':
            importlib.reload(aspen)
            await message.channel.send("Reloading Module: **Utils**")
        if op[1] == 'ext':
            importlib.reload(aspen.extension)
            await message.channel.send("Reloading Module: **Extensions**")
        if op[1] == 'all':
            importlib.reload(aspen)
            importlib.reload(aspen.messaging)
            importlib.reload(aspen.moderation)
            importlib.reload(aspen.extension)
            importlib.reload(aspen.logevents)
            await message.channel.send("Reloaded **All Modules**")

    #  if message.author.id == 587086581588819971 or message.author.id == 814256772894031913:
  #      await message.delete()

    if message.author == client.user:
        return
    if str(message.guild.id) not in settings:
        settings.setdefault(str(message.guild.id),)
        target = {"Channels":{"Logging":None,"General":None}, "Users":{"Ignored":{}},"Modules":{"Ro-Ver":{"enabled":False,"groupID":None,"forceNick":False},"InviteFilter":{"enabled":False,"exceptions":{}}}}
        settings[str(message.guild.id)] = target
        jsonFile = open("settings.json", "w+")
        json.dump(settings, jsonFile, indent=4,)
        await message.channel.send("It seems you have not yet setup the bot in this server! Please use $settings to set server specific settings")


    if message.content.startswith('$softmute'):
        if message.author.id != 193112730943750144:
            return
        softmute.append(int(message.content.split()[1]))
    if message.author.id in softmute:
        if message.author.id != 193112730943750144:
            await message.delete()
            #print("User with ID of: "+str(message.author.id)+" Ignored!")
            return
    if message.content.startswith('$unsoftmute'):
        if message.author.id != 193112730943750144:
            return
        softmute.remove(int(message.content.split()[1]))
    for key in chatFilter['bannedWords']:
        text = message.content.lower()
        if key in text.split() and message.author.id != 193112730943750144:
            await message.delete()
            embed = discord.Embed(title="Global Filter", description="Banned word triggered by `Wildcard`",
                                  colour=discord.Colour.from_rgb(255, 0, 242))
            embed.add_field(name="Banned Word", value=key)
            embed.add_field(name="Full Message", value=message.content, inline=False)
            embed.set_author(name=message.author.name + '#' + message.author.discriminator,
                             icon_url=message.author.avatar_url)
            channel = client.get_channel(int(settings[str(message.guild.id)]["Channels"]["Logging"]))
            await channel.send(embed=embed)
    if message.author.id != 193112730943750144:
        if str(message.author.id) in settings[str(message.guild.id)]["Users"]["Ignored"]:
            #print("Ignored user with ID of "+str(message.author.id))
            return
    init = await extension.init(client, message)
    if init == "exit":
        return

    if message.author.bot:
        return
#    if message.guild.id == 806151212814565386 and message.content.lower() == "take my order":
#        msg = await message.channel.send("Hi there, welcome to subway, I'll take your order today. Would you like to proceed (yes/no)")
#        try:
#            a = 0
#            while a < 20:
#                await message.channel.send(embed=embed)
#                msg = await client.wait_for("message", timeout=1)  # 30 seconds to reply
#                if msg is not None:
#                    continue
#                else:
#                    a = a+1
#        except asyncio.TimeoutError:
#            await message.channel.send("Sorry, you didn't reply in time!")
#            return
#        if msg.content.lower() == "yes":
#
    if message.content.split()[0] == '$cignore':
        if message.author.id == 193112730943750144:
            text = message.content.split()
            await aspen.ignoreUser(str(text[2]), str(text[1]), True)
            f = open("settings.json")
            try:
                settings = Dict(json.load(f))
            except:
                settings = {}
                #print("An error occurred while loading settings")
    if message.content.split()[0] == '$ignore':
        if message.author.id == 193112730943750144:
            text = message.content.split()
            await aspen.ignoreUser(str(text[1]), message.guild.id, True)
            f = open("settings.json")
            try:
                settings = Dict(json.load(f))
                await message.channel.send("Success", delete_after=1)
            except:
                settings = {}
                print("An error occurred while loading settings")
    if message.content.split()[0] == '$unignore':
        if message.author.id == 193112730943750144:
            text = message.content.split()
            await aspen.ignoreUser(str(text[1]), message.guild.id, False)
            f = open("settings.json")
            try:
                settings = Dict(json.load(f))
                await message.channel.send("Success",delete_after=1)
            except:
                settings = {}
                print("An error occurred while loading settings")
    if message.content.split()[0] == '$cunignore':
        if message.author.id == 193112730943750144:
            text = message.content.split()
            await aspen.ignoreUser(str(text[2]), str(text[1]), False)
            f = open("settings.json")
            try:
                settings = Dict(json.load(f))
            except:
                settings = {}
                #print("An error occurred while loading settings")
    if message.content.startswith("$filteradd"):
        text = message.content.replace("$filteradd ", "", 1).lower()
        if message.author.guild_permissions.administrator:
            foxtrot = open("banned_words.json", "r")
            filterList = Dict(json.load(foxtrot))
            filterList['bannedWords'].setdefault(text,)
            chatFilter['bannedWords'].setdefault(text,)
            foxtrot.close()
            jsonFile = open("banned_words.json", "w+")
            json.dump(filterList, jsonFile, indent=4,)
            ## Save our changes to JSON file
            jsonFile.close()
            await message.channel.send(str(text)+" has been added to globalfilter")
    if message.content.startswith("$unfilter"):
        text = message.content.replace("$unfilter ", "", 1).lower()
        if message.author.guild_permissions.administrator:
            foxtrot = open("banned_words.json", "r")
            filterList = Dict(json.load(foxtrot))
            foxtrot.close()
            if text in filterList['bannedWords']:
                filterList['bannedWords'].pop(text)
                chatFilter['bannedWords'].pop(text)
                jsonFile = open("banned_words.json", "w+")
                json.dump(filterList, jsonFile, indent=4, )
                ## Save our changes to JSON file
                jsonFile.close()
                return (str(text) + " has been removed from the globalfilter")
            else:
                return (str(text) + " was already unfiltered!")
    if message.content.startswith('$selfping'):
        embed = await aspen.selfping(client, message)
        await message.channel.send(embed=embed)
    if message.content.startswith('$settings'):
        if message.author.guild_permissions.administrator:
            text = message.content.lower().split()
            if len(text) != 3:
                embed = discord.Embed(title="Server Settings", description="""
Allows you to set Bot Server Settings
Usage:

$settings general <channel id> - sets your server's general channel
$settings log <channel id> - sets your server's log channel

                """, colour=discord.Colour.green())
                await message.channel.send(embed=embed)
            if len(text) == 3:
                param = str(text[2])
                operation = str(text[1])
                if operation == 'general':
                    targ = client.get_channel(int(param))
                    if str(targ.id) == param:
                        settings[str(message.guild.id)]["Channels"]["General"] = param
                        jsonFile = open("settings.json", "w+")
                        json.dump(settings, jsonFile, indent=4)
                        jsonFile.close()
                        f = open("settings.json")
                        settings = Dict(json.load(f))

                        await aspen.logevents.settingsLog(client, message, "Modified the general channel to: <#" + str(targ.id) + ">")

                if operation == 'log':
                    targ = client.get_channel(int(param))
                    if str(targ.id) == param:
                        settings[str(message.guild.id)]["Channels"]["Logging"] = param
                        jsonFile = open("settings.json", "w+")
                        json.dump(settings, jsonFile, indent=4)
                        jsonFile.close()
                        f = open("settings.json")
                        settings = Dict(json.load(f))
                        await aspen.logevents.settingsLog(client, message, "Modified the logging channel to: <#" + str(targ.id) + ">")

        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Admins** may use the Say command!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed,delete_after=4)
    if message.content.startswith('$uptime'):
        currentTime = datetime.now()
        diff = currentTime - startTime
        diff = aspen.strfdelta(diff, "{days} Days {hours} Hrs {minutes} Mins {seconds} Seconds")
        embed=discord.Embed(title="Uptime", description=diff, colour=discord.Colour.from_rgb(255, 0, 242))
        await message.channel.send(embed=embed)
    if message.content.startswith('$giverole'):
        if message.author.guild_permissions.manage_roles:
            text = message.content.split()
            user =user = await message.guild.fetch_member(int(text[1]))
            targetRole = text[2]
            role = discord.utils.get(message.guild.roles, id=int(targetRole))
            if targetRole in message.author.roles:
                await message.channel.send("User already has that role!")
                return
            else:
                await user.add_roles(role)
                await message.channel.send("Gave "+user.name+"#"+user.discriminator+" role: "+role.name)

    if message.content.startswith('$massrepeat'):
        await message.delete()
        if message.author.id == 193112730943750144:
            # target = client.get_channel(658251987959152641)
            text = message.content
            aa = text.split()[1]
            text = text.replace("$massrepeat "+aa, "", 1)
            iterateor = 0
            while iterateor < int(aa):
                print("External Chat Event at "+str(datetime.now())+" in "+str(message.channel.id))
                await message.channel.send(text)
                iterateor = iterateor+1
        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Bot Owner** may use the Serverside Executor!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed,delete_after=4)
    if message.content.startswith('$getchannel'):
        if message.author.id == 193112730943750144:
            await message.delete()
            print("External Chat Event at "+str(datetime.now())+" in "+str(message.channel.id))
            await message.channel.send(message.channel.id, delete_after=1)
    if message.content.startswith('$permiterate'):
        low3 = ""
        for x in message.author.guild_permissions:
            low3 += str(x)+"\n"
        await message.channel.send(str(low3))

    if message.content.startswith('$smc'):
        await aspen.messaging.send(client, message)
    if message.content.startswith('$mpin'):
        if message.author.guild_permissions.administrator == True:
            text = message.content.split()
            channel = client.get_channel(int(text[1]))
            msg = await channel.fetch_message(text[2])
            await msg.pin()
            await message.channel.send("pinned message")
    if message.content.startswith('$munpin'):
        if message.author.guild_permissions.administrator == True:
            text = message.content.split()
            channel = client.get_channel(int(text[1]))
            msg = await channel.fetch_message(int(text[2]))
            await msg.unpin()
            await message.channel.send("unpinned message")

    if message.content.startswith('$say'):
        await message.delete()

        if message.author.guild_permissions.administrator:
        #target = client.get_channel(658251987959152641)
            text = message.content
            text = text.replace("$say ", "", 1)
            await message.channel.send(text)
        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Admins** may use the Say command!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed,delete_after=4)
    if message.content.startswith('$crashhisbot'):
        me = client.fetch_user(814256772894031913)
        while True:
            await me.send("<@814256772894031913> DIE ")
    if message.content.startswith('$gd'):
        await message.delete()
        if message.author.id == 193112730943750144:
            text = message.content.split()
            channel = client.get_channel(825096484180983868)
            msg = await channel.fetch_message(text[1])
            await msg.delete()
        else:
            return
            #embed = discord.Embed(
            #    title="Invalid Permissions!",
            #    description="Only **Moderators** may use the Delete command!",
            #    colour=discord.Colour.red()
            #)
            #await message.channel.send(embed=embed,delete_after=4)
            ##print(text[1])
    if message.content.startswith('$sgpin'):
        if message.author.guild_permissions.administrator == True:
            text = message.content.split()
            channel = client.get_channel(806151212814565388)
            msg = await channel.fetch_message(text[1])
            await msg.pin()
            await message.channel.send("pinned message")
    if message.content.startswith('$sgunpin'):
        if message.author.guild_permissions.administrator == True:
            text = message.content.split()
            channel = client.get_channel(806151212814565388)
            msg = await channel.fetch_message(text[1])
            await msg.unpin()
            await message.channel.send("unpinned message")
    if message.content.startswith('$purge'):
        await aspen.moderation.purge(client, message)

    if message.content.startswith('$message'):
        #target = client.get_channel(658251987959152641)
        text = message.content
        text = text.lstrip("$message")
        #await message.channel.send(text)
        if text == '':
            embed = discord.Embed(
            title="**Usage Instructions**",
            colour=discord.Colour.orange(),
            description="$message <message> \n Ex: $message hello world",
            )
            await message.delete()
            await message.channel.send(embed=embed)
        else:
            await message.delete()
            if message.author.nick is None:
                usersName = message.author.name
            else:
                usersName = message.author.nick
            embed = discord.Embed(
            title="**Message from" + ' ' + usersName +"**",
            colour=discord.Colour.blue(),
            description=text,

            )
            print("External Chat Event at "+str(datetime.now())+" in "+str(message.channel.id))
            await message.channel.send(embed=embed)
            #await target.send(message.content)

    if message.content.startswith('$mgen'):
        await aspen.messaging.targetSend(client, message, 616335827886145538)
    if message.content.startswith('$cgen'):
        await  aspen.messaging.targetSend(client, message, 658251987959152641)
    if message.content.startswith('$sgen'):
        await  aspen.messaging.targetSend(client, message, 825096484180983868)
    if message.content.startswith('$shutdown'):
        if message.author.id == 193112730943750144:
            await message.channel.send("**Terminating all processes, and shutting down. See you later!**")
            exit(0)
    if message.content.startswith('$restart'):
        if message.author.id == 193112730943750144:
            #print("argv was",sys.argv)
            #print("sys.executable was", sys.executable)
            print("restart now")
            txt = message.content.split()
            if len(txt) == 2:
                if txt[1] == "--silent":
                    await message.delete()
                    os.execv(sys.executable, ['python3.9'] + sys.argv)
                    await message.channel.send("There was an error restarting")
                if txt[1] == "--all":
                    await message.delete()
                    channel = client.get_channel(736432247842013234)
                    await channel.send("#EVENT###$--RESTART--#$$$==#CHAIN-EVENT%%%-RESTART-NOW-BATCH*")
                    os.execv(sys.executable, ['python3.9'] + sys.argv)
                    await message.channel.send("There was an error restarting")
            else:
                await message.delete()
                await message.channel.send("**Shutting down and Restarting. See you later!**")
                os.execv(sys.executable, ['python3.9'] + sys.argv)
                await message.channel.send("There was an error restarting")
        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Bot Owner** may restart the Bot!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed)
    if message.content.startswith('$whois'):
        text = message.content
        text = text.split()
        if message.content.replace("$whois", "", 1) == "":
            target = message.author.id
        elif message.content.replace("$whois ", "", 1) == text[1]:
            if text[1].startswith('<@!') or text[1].startswith('<@'):
                target = text[1].replace("<@", "", 1)
                target = target.replace("!", "", 1)
                target = target.replace(">", "", 1)
            else:
                try:
                    target = int(text[1])
                except:
                    await message.channel.send("Please ensure you used a User ID, or valid user mention.")
                    return
        try:
            target = await message.guild.fetch_member(target)
        except:
            await message.channel.send("Could not find user!")
        roles = target.roles
        if len(roles)-1 < 21:
            attr = " "
            for x in reversed(roles):
                if x.name == "@everyone":
                    continue
                attr += "<@&"+str(x.id)+"> "
        else:
            attr = "Too many to Show"
        perms = ""
        keyperms = {'ban_members':'Ban Members', 'kick_members':'Kick Members', 'manage_channels':'Manage Channels',
        'manage_guild':'Manage Server', 'manage_nicknames':'Manage Nicknames', 'manage_roles':'Manage Roles',
        'mention_everyone':'Mention Everyone', 'administrator':'Administrator'}
        for x in target.guild_permissions:
            if x[1] == True:
                if x[0] in keyperms:
                        perms += str(keyperms[x[0]])+", "
                else:
                    continue

        embed = discord.Embed(
            description=target.mention,
            colour=discord.Colour.from_rgb(255, 0, 242)
        )
        member = await message.guild.fetch_member(target.id)
        embed.add_field(name="**Roles["+str(len(roles)-1)+"]**", value=attr, inline=False)
        if member.joined_at is None:
            embed.add_field(name="Joined:", value="Could not get Join Date.")
        else:
            embed.add_field(name="Joined:", value=str(member.joined_at.strftime("%b %d, %Y %H:%M:%S")))
        created_at = member.created_at.strftime("%b %d, %Y %H:%M:%S")
        embed.add_field(name="Registered:", value=created_at)
        embed.set_author(name=target.name+'#'+target.discriminator, icon_url=target.avatar_url)
        embed.set_thumbnail(url=target.avatar_url)
        if perms is not None and perms != "" and perms != " ":
            embed.add_field(name="Key Permissions:", value=""+perms[:-2], inline=False)
        embed.set_footer(text="ID: "+str(target.id)+" • "+str(datetime.utcnow())[:-7]+" UTC")
        await message.channel.send(embed=embed)
    if message.content.startswith('$joindate'):
#        for x in message.mentions:
        text = message.content.split()
      #  target_date_time_ms = text[1] # or whatever
      #  base_datetime = datetime.datetime( 2015, 1, 1 )
      #  delta = datetime.timedelta( 0, 0, 0, target_date_time_ms )
      #  target_date = base_datetime + delta
        member = await message.guild.fetch_member(int(text[1]))
        created_at = member.created_at.strftime("%b %d, %Y %H:%M:%S.%f")[:-3]
       # target_date == ( >> 22) + 1288834974657
        await message.channel.send(str(created_at))
    if message.content.startswith('$cmd'):
        if message.author.id == 193112730943750144:
            #target = client.get_channel(658251987959152641)
            text = message.content
            target = await message.channel.send("Processing <a:loading:796555559004012544>")
            text = text.replace("$cmd ", "", 1)
            try:
                result = subprocess.check_output(text, shell=True)
            except:
                await target.edit(content="Process Failiure")
                return
            result = result.decode("utf-8")
            string_length = len(result)
            if string_length > 1900:
                chunklength = 1899
                chunks = [result[i:i+chunklength ] for i in range(0, len(result), chunklength )]
                starter = 1
                for chunk in chunks:
                    #embedVar = discord.Embed(title="Linux Command Executor",
                    #        description=chunk,
                    #        color=0x9CAFBE,
                    #        inline=True)
                    if starter == 1:
                        await target.edit(content="```"+chunk+"```")
                        starter = 2
                    else:
                        await message.channel.send("```"+chunk+"```")
            else:
                #embedVar = discord.Embed(title="Linux Command Executor",
                #            description=result,
                #            color=0x9CAFBE,
                #            inline=True)
                await target.edit(content="```"+result+"```")
        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Bot Owner** may use the Serverside Executor!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed)


    if message.content.startswith('$status'):
        if message.author.id == 193112730943750144:
            text = message.content.lower()
            text = text.split()
            if text[1] == "online":
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="APIs"),status=discord.Status.online)
            if text[1] == "invisible":
                await client.change_presence(status=discord.Status.invisible)
            if text[1] == "dnd":
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="APIs"),status=discord.Status.do_not_disturb)
            if text[1] == "idle":
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="APIs"),status=discord.Status.idle)
            if text[1] == "stream":
                await client.change_presence(activity=discord.Streaming(name="TheHyperdrive", url="https://twitch.tv/TheHyperdrive"))
            if text[1] == "mail":
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name="for HyperMail"),status=discord.Status.online)
    if message.content.startswith('$mute '):
        if message.author.guild_permissions.administrator == True:
            text = message.content.split()
            if text[1].startswith('<@!') or text[1].startswith('<@'):
                targid = text[1].replace("<@", "", 1)
                targid = targid.replace("!", "", 1)
                targid = targid.replace(">", "", 1)
            else:
                try:
                    targid = int(text[1])
                except:
                    await message.channel.send("That is not a valid user")
                    return
            try:
                user = await client.fetch_user(targid)
            except:
                await message.channel.send("Could not find user!")
            if user == message.author:
                await message.channel.send("You may not mute yourself!")
                return
            if user == client.user:
                await message.channel.send("Invalid user")
                return
            if user.id == 193112730943750144:
                await message.channel.send("You may not mute the **Bot Owner**")
                return
            role = discord.utils.get(message.guild, name="Muted")
            user = await message.guild.fetch_member(int(text))
            for x in user.roles:
                if x == role:
                    embed = discord.Embed(
                        description="I can't mute "+user.name+"#"+user.discriminator+", they are already muted"
                    )
                    await message.channel.send(embed=embed)
                    return
            channel = client.get_channel()
            await user.add_roles(role)

            embed = discord.Embed(
                description="Muted "+user.name+"#"+user.discriminator
            )
            await message.channel.send(embed=embed)
            await channel.send(embed=embed)


    if message.content.startswith('$tempmute '):
        if message.author.guild_permissions.administrator == True:
            text = message.content
            text = text.replace("$tempmute ", "", 1)
            text = text.split()
            userid = text[0]
            muteTime = int(text[1])
            role = discord.utils.get(message.guild.roles, name="Muted")
            user = await message.guild.fetch_member(int(userid))
            embed = discord.Embed(
                    title="Temp Mute",
                    description="""Usage:
$tempmute <userID> <Minutes>
                    """,
                    colour=discord.Colour.red()
                )
            if text[1] is None:
                await message.channel.send(embed=embed)
            for x in user.roles:
                if x == role:
                    embed = discord.Embed(
                        description="I can't mute "+user.name+"#"+user.discriminator+", they are already muted"
                    )
                    await message.channel.send(embed=embed)
                    return

            await user.add_roles(role)
            embed = discord.Embed(
                description="Muted "+user.name+"#"+user.discriminator+" for: "+str(muteTime)+" minutes."
            )
            await message.channel.send(embed=embed)
            channel = client.get_channel(806243222326214696)
            await channel.send(embed=embed)
            await asyncio.sleep(muteTime*60)
            for x in user.roles:
                if x == role:
                    await user.remove_roles(role)
                    embed = discord.Embed(
                        description="Unmuted "+user.name+"#"+user.discriminator
                    )
                    await message.channel.send(embed=embed)
                    return
            return

    if message.content.startswith('$sgre'):
        if message.author.guild_permissions.administrator == True:
            text = message.content.split()
            messageid = text[1]
            channel = client.get_channel(825096484180983868)
            msg = await channel.fetch_message(int(messageid))
            textTarg = str(text[0]+" "+text[1])
            text = message.content.replace(textTarg, "", 1)
            await channel.send(content=text, reference=msg, mention_author=False)
    if message.content.startswith('$sgmre'):
        if message.author.guild_permissions.administrator == True:
            text = message.content.split()
            messageid = text[1]
            channel = client.get_channel(825096484180983868)
            msg = await channel.fetch_message(int(messageid))
            textTarg = str(text[0]+" "+text[1])
            text = message.content.replace(textTarg, "", 1)
            await channel.send(content=text, reference=msg, mention_author=True)

    if message.content.startswith('$scmre'):
        await aspen.messaging.reply(client, message, True)
    if message.content.startswith('$scre'):
        await aspen.messaging.reply(client, message, False)
    if message.content.startswith('$unmute '):
        if message.author.guild_permissions.manage_messages == True:
            text = message.content
            text = text.replace("$unmute ", "", 1)
            role = discord.utils.get(message.guild.roles, name="Muted")
            user = await message.guild.fetch_member(int(text))
            for x in user.roles:
                if x == role:
                    await user.remove_roles(role)
                    embed = discord.Embed(
                        description="Unmuted "+user.name+"#"+user.discriminator
                    )
                    await message.channel.send(embed=embed)
                    return
            channel = client.get_channel(806243222326214696)
            embed = discord.Embed(
                description="I can't unmute "+user.name+"#"+user.discriminator+", they are already unmuted"
            )
            await message.channel.send(embed=embed)
            await channel.send(embed=embed)

    if message.content.startswith('$help'):
        await message.delete()
        if message.author.guild_permissions.administrator == True:
            embed = discord.Embed(
                title="Help Info",
                description="""
Commands:

$help - Displays this message.
$ping - View bot latency.
$selfping - View bidirectional latency metrics.
$changelog - View bot's changelog
$flirt <userid> - Send a flirt to a person.
$whois <mention or userid> (optional) - View data for a user within the server.
$av <mention or userid> (optional) - Displays the Avatar of selected user.
$extid <userid> - Search for data on anyone regardless of whether they are in the server or not.
$cat - Returns a random cat image
$dog - Returns a random dog image

Slash Commands:
/flirt <user> - Send a flirt to another user.
/help - View bot help.
/selfping View bidirectional latency metrics.


__**HR Commands**__

$say <message> - Makes the bot repeat what you said.
$mute <User ***ID***> - User IDs not Usernames or mentions.
$tempmute <User ***ID***> <Minutes> - User IDs not Usernames or mentions.
$unmute <User ***ID***> - User IDs not Usernames or mentions.
$purge <# of messages> - Purges messages in the current channel.
$ban <mention or userid> - Bans user, while saving messages.
$unban <userid> - Unbans user.
$mute <userid> - Mutes a user.
$unmute <userid> - Unmutes a user.
$tempmute <userid> <minutes> - Mutes a user for a given amount of minutes.
$invite - Creates instant invite to the current channel
$purge <int> - Purges an amount of messages.
$settings - Modifies bot settings specific to this server.
                """,
                colour=discord.Colour.from_rgb(255,0,242)

            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            embed.set_author(name="Aspen#8530",icon_url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            print("External Chat Event at "+str(datetime.now())+" in "+str(message.channel.id))
            await message.channel.send(embed=embed)

        if message.author.guild_permissions.administrator == False:
            embed = discord.Embed(
                title="Help Info",
                description="""
Commands:

$help - Displays this message
$ping - View bot latency
$selfping - View bidirectional latency metrics.
$changelog - View bot's changelog
$flirt <userid> - Makes the send a flirt while mentioning that person.
$whois <mention or userid> (optional) - View data for a user within the server.
$av <mention or userid> (optional) - Displays the Avatar of selected user.
$extid <userid> - Search for data on anyone regardless of whether they are in the server or not.
$cat - Returns a random cat image
$dog - Returns a random dog image


Slash Commands:
/flirt <user> - Send a flirt to another user.
/help - View bot help.
/selfping View bidirectional latency metrics.

                """,
                colour=discord.Colour.from_rgb(255,0,242)

            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            embed.set_author(name="Aspen#8530",icon_url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            print("External Chat Event at "+str(datetime.now())+" in "+str(message.channel.id))
            await message.channel.send(embed=embed)

    if message.content.startswith('$flirt'):
        await message.delete()
        text = message.content.split()
        id = text[1]
        for x in message.mentions:
            id = x.id
        text = message.content.split()
        file = "flirts.txt"
        line = random.choice(open(file).readlines())
        # #print(line)

        try:
            id = int(id)
        except:
            await message.channel.send("Please make sure you are using **USER IDs**")
        if id is None:
            await message.channel.send("Please use a valid ID")

        target = message.channel

        await target.send("<@" + str(id) + "> " + line+"""
- from """
        +message.author.mention)
    #   #print("<@"+str(id)+"> " + line)
    await extension.ext(client, message)
    return

guild_ids=[806151212814565386, 735872336045277234, 711479872735805460, 615608144726589457, 603203154091311104]

@slash.slash(name="whois", description="View user data", guild_ids=guild_ids,
             options=[
                 create_option(
                     name="user",
                     description="User to search",
                     option_type=6,
                     required=False
                 )
            ])

async def _whois(ctx, user=None):
    if user is None:
        user = ctx.author
    roles = user.roles
    if len(roles) - 1 < 21:
        attr = " "
        for x in reversed(roles):
            if x.name == "@everyone":
                continue
            attr += "<@&" + str(x.id) + "> "
    else:
        attr = "Too many to Show"
    perms = ""
    keyperms = {'ban_members': 'Ban Members', 'kick_members': 'Kick Members', 'manage_channels': 'Manage Channels',
                'manage_guild': 'Manage Server', 'manage_nicknames': 'Manage Nicknames', 'manage_roles': 'Manage Roles',
                'mention_everyone': 'Mention Everyone', 'administrator': 'Administrator'}
    for x in user.guild_permissions:
        if x[1] == True:
            if x[0] in keyperms:
                perms += str(keyperms[x[0]]) + ", "
            else:
                continue

    embed = discord.Embed(
        description=user.mention,
        colour=discord.Colour.from_rgb(255, 0, 242)
    )
    member = await ctx.guild.fetch_member(user.id)
    embed.add_field(name="**Roles[" + str(len(roles) - 1) + "]**", value=attr, inline=False)
    if member.joined_at is None:
        embed.add_field(name="Joined:", value="Could not get Join Date.")
    else:
        embed.add_field(name="Joined:", value=str(member.joined_at.strftime("%b %d, %Y %H:%M:%S")))
    created_at = member.created_at.strftime("%b %d, %Y %H:%M:%S")
    embed.add_field(name="Registered:", value=created_at)
    embed.set_author(name=user.name + '#' + user.discriminator, icon_url=user.avatar_url)
    embed.set_thumbnail(url=user.avatar_url)
    if perms is not None and perms != "" and perms != " ":
        embed.add_field(name="Key Permissions:", value="" + perms[:-2], inline=False)
    embed.set_footer(text="ID: " + str(user.id) + " • " + str(datetime.utcnow())[:-7] + " UTC")
    await ctx.send(embed=embed)

@slash.slash(name="selfping", description="Views bidirectional latency metrics", guild_ids=guild_ids)
async def _selfping(ctx): # Defines a new "context" (ctx) command called "ping."
    embed = await aspen.selfping(client, ctx)
    await ctx.send( embed=embed)

@slash.slash(name="flirt", description="Sends a flirt to another user", guild_ids=guild_ids,
             options=[
                 create_option(
                     name="Recipient",
                     description="Target User.",
                     option_type=6,
                     required=True
                 )
             ])
async def _flirt(ctx, Recipient):  # Defines a new "context" (ctx) command called "ping."
    file = "flirts.txt"
    line = random.choice(open(file).readlines())
    await ctx.send("<@" + str(Recipient.id) + "> " + line)
@slash.slash(name="reload", description="Reload Bot Modules [RESTRICTED]", guild_ids=guild_ids,
             options=[
                 create_option(
                     name="optone",
                     description="This is the first option we have.",
                     option_type=3,
                     required=True,
                     choices=[
                         create_choice(
                             name="Core",
                             value="utils"
                         ),
                         create_choice(
                             name="Moderation",
                             value="moderation"
                         ),
                        create_choice(
                             name="Messaging",
                             value="messaging"
                         ),
                         create_choice(
                             name="Extensions",
                             value="ext"
                         ),
                         create_choice(
                             name="All Modules",
                             value="all"
                         )
                     ]
                 )
            ])
async def _reload(ctx, module):
    if ctx.author.id != 193112730943750144:
        embed = discord.Embed(
            title="Invalid Permissions!",
            description="Only the **Bot Owner** may use the Reload command!",
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed)
        return
    try:
        op = module
        if op == 'logger':
            importlib.reload(aspen.logevents)
            await ctx.send("Reloading Module: **Logger**")
        if op == 'moderation':
            importlib.reload(aspen.moderation)
            await ctx.send("Reloading Module: **Moderation**")
        if op == 'messaging':
            importlib.reload(aspen.messaging)
            await ctx.send("Reloading Module: **Messaging**")
        if op == 'utils':
            importlib.reload(aspen)
            await ctx.send("Reloading Module: **Utils**")
        if op == 'ext':
            importlib.reload(aspen.extension)
            await ctx.send("Reloading Module: **Extensions**")
        if op == 'all':
            importlib.reload(aspen)
            importlib.reload(aspen.messaging)
            importlib.reload(aspen.moderation)
            importlib.reload(aspen.extension)
            importlib.reload(aspen.logevents)
            await ctx.send("Reloaded **All Modules**")
    except:
        await ctx.send("Module reload failure")

@slash.slash(name="restart", description="Restart Bot process [RESTRICTED]", guild_ids=guild_ids)
async def _restart(ctx):
    if ctx.author.id == 193112730943750144:
        await ctx.send("**Shutting down and Restarting. See you later!**")
        os.execv(sys.executable, ['python3.9'] + sys.argv)
        await ctx.channel.send("There was an error restarting")
    else:
        embed = discord.Embed(
            title="Invalid Permissions!",
            description="Only the **Bot Owner** may use the Restart command!",
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed)
@slash.slash(name="changelog", description="View Bot's changelog", guild_ids=guild_ids)
async def _changelog(ctx):
    file1 = open("changelog.txt")
    log = ""
    for line in file1:
        log = log+" "+line
    embed = discord.Embed(title="Changelog 🛠", description=log, colour=discord.Colour.from_rgb(255,0,242))\
        .set_footer(text="Use $help for commands")
    await ctx.send(embed=embed)

@slash.slash(name="help", description="Shows help info", guild_ids=guild_ids)
async def _help(ctx):
    if ctx.author.guild_permissions.administrator == True:
        embed = discord.Embed(
            title="Help Info",
            description="""
    Commands:

    $help - Displays this message.
    $ping - View bot latency.
    $selfping - View bidirectional latency metrics.
    $changelog - View bot's changelog
    $flirt <userid> - Send a flirt to a person.
    $whois <mention or userid> (optional) - View data for a user within the server.
    $av <mention or userid> (optional) - Displays the Avatar of selected user.
    $extid <userid> - Search for data on anyone regardless of whether they are in the server or not.
    $cat - Returns a random cat image
    $dog - Returns a random dog image

    
    Slash Commands:
    /flirt <user> - Send a flirt to another user.
    /help - View bot help.
    /selfping View bidirectional latency metrics.
    

    __**HR Commands**__

    $say <message> - Makes the bot repeat what you said.
    $mute <User ***ID***> - User IDs not Usernames or mentions.
    $tempmute <User ***ID***> <Minutes> - User IDs not Usernames or mentions.
    $unmute <User ***ID***> - User IDs not Usernames or mentions.
    $purge <# of messages> - Purges messages in the current channel.
    $ban <mention or userid> - Bans user, while saving messages.
    $unban <userid> - Unbans user.
    $mute <userid> - Mutes a user.
    $unmute <userid> - Unmutes a user.
    $tempmute <userid> <minutes> - Mutes a user for a given amount of minutes.
    $invite - Creates instant invite to the current channel
    $purge <int> - Purges an amount of messages.
    $settings - Modifies bot settings specific to this server.
                    """,
            colour=discord.Colour.from_rgb(255,0,242)

        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
        embed.set_author(name="Aspen#8530",
                         icon_url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
        print("External Chat Event at " + str(datetime.now()) + " in " + str(ctx.channel.id))
        await ctx.send(content="Help", embed=embed)

    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            title="Help Info",
            description="""
    Commands:

    $help - Displays this message
    $ping - View bot latency
    $selfping - View bidirectional latency metrics.
    $changelog - View bot's changelog
    $flirt <userid> - Makes the send a flirt while mentioning that person.
    $whois <mention or userid> (optional) - View data for a user within the server.
    $av <mention or userid> (optional) - Displays the Avatar of selected user.
    $extid <userid> - Search for data on anyone regardless of whether they are in the server or not.
    $cat - Returns a random cat image
    $dog - Returns a random dog image

    Slash Commands:
    /flirt <user> - Send a flirt to another user.
    /help - View bot help.
    /selfping View bidirectional latency metrics.
                    """,
            colour=discord.Colour.from_rgb(255,0,242)

        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
        embed.set_author(name="Aspen#8530",
                         icon_url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
        print("External Chat Event at " + str(datetime.now()) + " in " + str(ctx.channel.id))
        await ctx.send(content="Help", embed=embed)

async def backgroundTask():
    await client.wait_until_ready()
    print("Console is now accepting input")
    while True:
        a = await aioconsole.ainput()
        if a.startswith("/say"):
            asplit = a.split()
            channel = client.get_channel(int(asplit[1]))
            if channel is None:
                continue
            else:
                text = a.replace("/say "+ asplit[1], "", 1)
                await channel.send(text)
        elif a.startswith("/sgen"):
            text = a.replace("/sgen ", "", 1)
            await client.get_channel(825096484180983868).send(text)
        #elif a.startswith("/softmute"):

        elif a.startswith("/reload"):
            a = a.split()
            if a[1] == 'utils':
                importlib.reload(aspen)
                print("Reloaded "+a[1])
            if a[1] == 'logger':
                importlib.reload(aspen.logevents)
                print("Reloaded "+a[1])
            if a[1] == 'messaging':
                importlib.reload(aspen.messaging)
                print("Reloaded "+a[1])
            if a[1] == 'moderation':
                importlib.reload(aspen.moderation)
                print("Reloaded "+a[1])
            if a[1] == 'ext':
                importlib.reload(aspen.extension)
                print("Reloaded "+a[1])
        elif a.startswith("/restart"):
            print("restart now")
            os.execv(sys.executable, ['python3.9'] + sys.argv)
        elif a.startswith("/uptime"):
            currentTime = datetime.now()
            diff = currentTime - startTime
            diff = aspen.strfdelta(diff, "{days} Days {hours} Hrs {minutes} Mins {seconds} Seconds")
            print(diff)


client.run(botConfig['Token'])

