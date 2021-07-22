import asyncio
import importlib
import json
import os
import random
import subprocess
import sys
from datetime import datetime

import aioconsole
import discord
import requests
from addict import Dict
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice

import aspen
from aspen import moderation, messaging, logevents, extension

debug = False
hyperid = 193112730943750144
loonaticid = 141314236998615040
# variables used throughout operations
startTime = datetime.now()
softmute = []  # userids in softmute get all of their messages deleted as soon as the bot is able to do so
channelmute = []
holder = []
sniper = {}
f = open("settings.json")
Intents = discord.Intents.default()
Intents.members = True
# client = commands.AutoShardedBot(command_prefix="$", intents=Intents, shard_count=3, shard_ids=[0, 1, 2])
client = commands.Bot(command_prefix="$", intents=Intents)
slash = SlashCommand(client, sync_commands=True)
settings = {}  # placeholder dict for settings in event of loading failure
try:
    settings = Dict(json.load(f))  # loads guild specific settings
    f.close()
except:
    print("An error occurred while loading settings")

  # banned words is currently a global filter, although will become a guild specific list soon
botConfig = Dict(json.load(open("config.json")))
embedColour = discord.Colour.from_rgb(255, 0, 242)


@client.event
async def on_disconnect():
    print('Bot has disconnected')
    os._exit(1)
    raise Exception("Bot failure")
    print("if you see this, the reload is broken")

@client.event
async def on_ready():  # run when all of the shards have logged in and connected
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="APIs"))
    client.loop.create_task(backgroundTask())  # fires the command line console input


@client.event
async def on_member_join(member):  # runs when a new user joins any guild that the bot is in
    global debug
    if member.bot:
        return
    if settings[str(member.guild.id)]["Modules"]["Welcome"]["enabled"]:
        channel = client.get_channel(int(settings[str(member.guild.id)]["Modules"]["Welcome"]["channel_id"]))
        content = str(settings[str(member.guild.id)]["Modules"]["Welcome"]["content"])
        if "{{user.mention}}" in content.lower():
            content = content.replace("{{user.mention}}", member.mention)
        await channel.send(content)
    return

@ client.event
async def on_member_update(before, after):
    return
@client.event
async def on_message_edit(before, after):  # run whenever a message is edited
    global debug
    global chatFilter
    if after.author == client.user:  # if the edited message is done by this bot, the message is deleted
        return
    if not await aspen.isOwner(after):
        if "discord.gg/" in after.content:  # need to add a guild setting check, which will allow guild admins to disable
            if not after.author.guild_permissions.manage_messages:
                await after.delete()
        for key in settings[str(after.guild.id)]["Modules"]["ChatFilter"]["BannedWords"]:  # checks for banned words as editing messages could be used as a bypass
            text = after.content.lower()
            if key in text.split() and not (after.author.id == hyperid or after.author.id == loonaticid):
                holder.append(after.id)
                await after.delete()
                embed = discord.Embed(title="Global Filter", description="Banned word triggered by `Match \n"+after.content,
                                      colour=discord.Colour.from_rgb(255, 0, 242))
                embed.add_field(name="Banned Word", value=key)
                embed.set_author(name=after.author.name + '#' + after.author.discriminator,
                                 icon_url=after.author.avatar_url)
                channel = client.get_channel(int(settings[str(after.guild.id)]["Channels"]["Logging"]))
                await channel.send(embed=embed)
        for key in settings[str(after.guild.id)]["Modules"]["ChatFilter"]["Wildcard"]:  # checks for banned words as editing messages could be used as a bypass
            if key in after.content.lower() and not await aspen.isOwner(after):
                holder.append(after.id)
                await after.delete()
                embed = discord.Embed(title="Global Filter", description="Banned word triggered by `Wildcard` \n"+after.content,
                                      colour=discord.Colour.from_rgb(255, 0, 242))
                embed.add_field(name="Banned Word", value=key)
                embed.set_author(name=after.author.name + '#' + after.author.discriminator,
                                 icon_url=after.author.avatar_url)
                channel = client.get_channel(int(settings[str(after.guild.id)]["Channels"]["Logging"]))
                await channel.send(embed=embed)


@client.event
async def on_message_delete(message):  # run whenever a message is deleted but is in the bot's cache
    global debug
    global sniper  # currently unused
    if message.author.id in softmute:
        return
    if message.author.bot:
        return
    if message.id in holder:
        return
    await aspen.logevents.deleteLog(client, message)  # creates a logged event in the guild's log channel, if one is set
    if str(message.channel.id) not in sniper:
        sniper.setdefault(str(message.channel.id), [])
    key = str(message.channel.id)
    value = message
    sniper[key] = [value] if key not in sniper else sniper[key] + [value]
    if len(sniper[key]) > 5:
        sniper[key].pop(0)


@client.event
async def on_message(message):  # runs asynchronously for each message sent that the bot can view
    global debug
    global softmute
    global channelmute
    global settings
    global chatFilter
    global sniper  # currently unused
    if message.type == discord.MessageType.pins_add:
        await message.delete()
    if message.author.id in softmute:
        if not await aspen.isOwner(message):
            await message.delete()
            # print("User with ID of: "+str(message.author.id)+" Ignored!")
            return
    if message.author == client.user:
        return
    if message.channel.id in channelmute:
        await message.delete()
    if message.guild != None and str(message.guild.id) not in settings:
        settings.setdefault(str(message.guild.id), )
        target = {"Channels": {"Logging": None, "General": None}, "Users": {"Ignored": {}},
                  "Modules": {"Ro-Ver": {"enabled": False, "groupID": None, "forceNick": False},
                              "InviteFilter": {"enabled": False, "exceptions": {}},
                              "Welcome": {"enabled": False, "content": None, "channel_id": None},
                              "ChatFilter":{"enabled":False, "exceptions":[], "BannedWords":[], "Wildcard":[]}}}
        settings[str(message.guild.id)] = target
        jsonfile = open("settings.json", "w+")
        json.dump(settings, jsonfile, indent=4, )
        await message.channel.send(
            "It seems you have not yet setup the bot in this server! Please use $settings to set server specific settings")
    if message.content is None:
        return

    if message.content.startswith('$reload'):  # allows for on-the-fly updates of modules without restarting the bot
        if message.author.id != 193112730943750144:
            await message.channel.send(embed=discord.Embed(title="Invalid Permissions",
                                                           description="Only the **Bot Owner** may use the Reload command",
                                                           colour=discord.Colour.red()))
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
    if debug:
        await message.channel.send("Author: "+str(message.author.id))
        await message.channel.send("Is Owner: " + str(await aspen.isOwner(message)))
    if not await aspen.isAdmin(message.author):
        if debug:
            sttime = datetime.utcnow()
#        role = discord.utils.get(message.guild.roles, name="On Watch")
#        if role in message.author.roles and message.author.guild_permissions.administrator == False:
#            if "http" in message.content.lower():
#                await message.delete()
#                channel = client.get_channel(int(settings[str(message.guild.id)]["Channels"]["Logging"]))
#                embed = discord.Embed(
#                    title="Global Filter",
#                    description="Banned word triggered by `On-Watch link remover`",
#                    colour=discord.Colour.from_rgb(255, 0, 242)
#                )
#                embed.add_field(name="Trigger", value="Link Posted")
#                embed.add_field(name="Full Message", value=message.content, inline=False)
#                embed.set_author(name=message.author.name+'#'+message.author.discriminator, icon_url=message.author.avatar_url)
#                await channel.send(embed=embed)
        for key in settings[str(message.guild.id)]["Modules"]["ChatFilter"]["BannedWords"]:  # checks for banned words
            text = message.content.lower()
            if key in text.split():
                holder.append(message.id)
                await message.delete()
                embed = discord.Embed(title="Global Filter", description="Banned word triggered by `Match` \n"+message.content,
                                      colour=discord.Colour.from_rgb(255, 0, 242))
                embed.add_field(name="Banned Word", value=key)
                embed.set_author(name=message.author.name + '#' + message.author.discriminator,
                                 icon_url=message.author.avatar_url)
                channel = client.get_channel(int(settings[str(message.guild.id)]["Channels"]["Logging"]))
                await channel.send(embed=embed)
                if debug:
                    ntime = datetime.utcnow()
                    diff = ntime - sttime
                    elapsed_time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
                    elapsed_time = str(elapsed_time)
                    await message.channel.send("ran banword filter check in " + elapsed_time + " ms")
                    await message.channel.send("DEBUG: Automod Deleted message due to key: " + key)
                return
        if debug:
            ntime = datetime.utcnow()
            diff = ntime - sttime
            elapsed_time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
            elapsed_time = str(elapsed_time)
            await message.channel.send("ran banword filter check in " + elapsed_time +" ms")

        for key in settings[str(message.guild.id)]["Modules"]["ChatFilter"]["Wildcard"]:  # checks for banned words
            text = message.content.lower()
            if key in text and not await aspen.isAdmin(message.author):
                holder.append(message.id)
                await message.delete()
                embed = discord.Embed(title="Global Filter", description="Banned word triggered by `Wildcard`\n"+message.content,
                                      colour=discord.Colour.from_rgb(255, 0, 242))
                embed.add_field(name="Banned Word", value=key)
                embed.set_author(name=message.author.name + '#' + message.author.discriminator, icon_url=message.author.avatar_url)
                channel = client.get_channel(int(settings[str(message.guild.id)]["Channels"]["Logging"]))
                await channel.send(embed=embed)
                if debug:
                    await message.channel.send("DEBUG: Automod Deleted message due to key: " + key)
                    ntime = datetime.utcnow()
                    diff = ntime - sttime
                    elapsed_time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
                    elapsed_time = str(elapsed_time)
                    await message.channel.send("ran banword filter check in " + elapsed_time + " ms")
                return
        if debug:
            await message.channel.send(str(settings[str(message.guild.id)]["InviteFilter"]["enabled"]))

        if settings[str(message.guild.id)]["Modules"]["InviteFilter"]["enabled"] == True:
            if not await aspen.isAdmin(message.author):
                for x in ["discord.gg/", "discord.com/invite", "discordapp.com/invite",
                            "watchanimeattheoffice.com/invite", "discord.co/invite"]:
                    if x in message.content.lower():
                        await message.delete()
                        key = "Discord Invite Link"
                        await logevents.filterLog(client, message, key)
                        return
    if message.author.id != 193112730943750144:
        if str(message.author.id) in settings[str(message.guild.id)]["Users"]["Ignored"]:
            # print("Ignored user with ID of "+str(message.author.id))
            return
    if message.author.bot:
        return

    if debug:
        await message.channel.send(str(message.content.split()))
        print(message.content)
    if not message.content is None:
        command = message.content.lower().split()[0]

    if command == '$debug' and await aspen.isOwner(message):
        if debug:
            debug = False
            await message.channel.send("Debug Mode is Disabled.")
            print("DEBUG MODE DISABLED")
            return
        msg = await message.channel.send("""```
You are selecting to Activate the Debugger.
Debug Mode can be potentially dangerous, can hit rate limits, and mess chats, and other guilds.
Do you wish to proceed? [Y/n]
        ```""")

        def debcheck(m):
            if m.author == message.author:
                #print("True")
                return True
            else:
                #print("False")
                return False
        try:
            response = await client.wait_for('message', check=debcheck, timeout=10)
        except asyncio.TimeoutError:
            await message.delete()
            await msg.delete()
            await message.channel.send("You took too long to respond", delete_after=2)
            return
        # print(response.content.lower())
        await message.delete()
        yes = ['y', 'yes', 'true']
        for x in yes:
            #print(x)
            if x in response.content.lower():
                debug = True
                print("DEBUGGER ACTIVE!!")
                await response.delete()
                await msg.delete()
                await message.channel.send("Debug mode is now Active. Use $debug at anytime to deactivate.", delete_after=2)
                return
        no = ['n', 'no', 'false']
        for x in no:
            if x in response.content.lower():
                await response.delete()
                await msg.delete()
                await message.channel.send("Debug mode will remain disabled.", delete_after=2)
                return
        await response.delete()
        await msg.delete()
        await message.channel.send("You sent an invalid response.", delete_after=2)
        return

        debug = True
    if command == '$softmute':
        if not await aspen.isOwner(message):
            return
        channelmute.append(int(message.content.split()[1]))

    if command == '$unsoftmute':
        if not await aspen.isOwner(message):
            return
        channelmute.remove(int(message.content.split()[1]))
    if command == '$cm':
        if not await aspen.isOwner(message):
            return
        channelmute.append(int(message.content.split()[1]))

    if command == '$uncm':
        if not await aspen.isOwner(message):
            return
        channelmute.remove(int(message.content.split()[1]))
    #print(debug)
    initstat = await extension.init(client, message, command, debug)

    if initstat == "exit" or initstat == "Exit":
        if debug:
            await message.channel.send("`Terminated by Module: EXT`")
        return

    if command == "$ofd":
        await message.delete()
        if message.author.id == 193112730943750144:
            text = message.content.split()
            channel = client.get_channel(858406792468234244)
            msg = await channel.fetch_message(text[1])
            holder.append(msg.id)
            await msg.delete()
        else:
            return
    if command == '$cignore':
        if await aspen.isOwner(message):
            text = message.content.split()
            await aspen.ignoreUser(str(text[2]), str(text[1]), True)
            f = open("settings.json")
            try:
                settings = Dict(json.load(f))
            except:
                settings = {}
                message.channel.send("CRITICAL ERROR! CHECK JSON SETTINGS IMMEDIATELY TO PREVENT DAMAGE")
                # print("An error occurred while loading settings")
    if command == '$ignore':
        if await aspen.isOwner(message):
            text = message.content.split()
            await aspen.ignoreUser(str(text[1]), message.guild.id, True)
            f = open("settings.json")
            try:
                settings = Dict(json.load(f))
                await message.channel.send("Success", delete_after=1)
            except:
                settings = {}
                print("An error occurred while loading settings")
    if command == '$unignore':
        if await aspen.isOwner(message):
            text = message.content.split()
            await aspen.ignoreUser(str(text[1]), message.guild.id, False)
            f = open("settings.json")
            try:
                settings = Dict(json.load(f))
                await message.channel.send("Success", delete_after=1)
            except:
                settings = {}
                print("An error occurred while loading settings")
    if command == '$cunignore':
        if await aspen.isOwner(message):
            text = message.content.split()
            await aspen.ignoreUser(str(text[2]), str(text[1]), False)
            f = open("settings.json")
            try:
                settings = Dict(json.load(f))
            except:
                settings = {}
                # print("An error occurred while loading settings")
    if command == "$filteradd":
        text = message.content.lower().replace("$filteradd ", "", 1).lower()
        if await aspen.isAdmin(message.author):
            if "--debug" in text:
                text = text.replace("--debug", "", 1)
                await message.channel.send(text)
            if not settings[str(message.guild.id)]["Modules"]["ChatFilter"]["enabled"]:
                await message.delete()
                await message.channel.send(
                    "Chat filter is currently disabled in this server, use $settings module list for more details.",
                    delete_after=4)
                return
            if text in settings[str(message.guild.id)]["Modules"]["ChatFilter"]["BannedWords"]:
                await message.channel.send(text +" is already banned!")
                return
            settings[str(message.guild.id)]["Modules"]["ChatFilter"]["BannedWords"].append(text)
            jsonFile = open("settings.json", "w+")
            json.dump(settings, jsonFile, indent=4)
            jsonFile.close()
            f = open("settings.json")
            settings = Dict(json.load(f))
            await message.channel.send(str(text) + " has been added to chat filter")
            await aspen.logevents.settingsLog(client, message, "added "+ str(text)+ " to chat filter")
            return
    if command == "$wladd":
        text = message.content.replace("$wladd ", "", 1).lower()
        if await aspen.isAdmin(message.author):
            if text in settings[str(message.guild.id)]["Modules"]["ChatFilter"]["Wildcard"]:
                await message.channel.send(text +" is already wildcarded!")
                return
            if not settings[str(message.guild.id)]["Modules"]["ChatFilter"]["enabled"]:
                await message.delete()
                await message.channel.send(
                    "Chat filter is currently disabled in this server, use $settings module list for more details.",
                    delete_after=4)
                return
            settings[str(message.guild.id)]["Modules"]["ChatFilter"]["Wildcard"].append(text)
            jsonFile = open("settings.json", "w+")
            json.dump(settings, jsonFile, indent=4)
            jsonFile.close()
            f = open("settings.json")
            settings = Dict(json.load(f))
            await message.channel.send(str(text) + " has been added to Wildcard")
            await aspen.logevents.settingsLog(client, message, "added "+ str(text)+ " to Wildcard")
            return
    if command == "$unfilter":
        text = message.content.replace("$unfilter ", "", 1).lower()
        if await aspen.isAdmin(message.author):
            if not settings[str(message.guild.id)]["Modules"]["ChatFilter"]["enabled"]:
                await message.delete()
                await message.channel.send(
                    "Chat filter is currently disabled in this server, use $settings module list for more details.",
                    delete_after=4)
                return
            if text in settings[str(message.guild.id)]["Modules"]["ChatFilter"]["BannedWords"]:
                settings[str(message.guild.id)]["Modules"]["ChatFilter"]["BannedWords"].remove(text)
            else:
                await message.channel.send(text + " was already unfiltered!")
                return
            jsonFile = open("settings.json", "w+")
            json.dump(settings, jsonFile, indent=4)
            jsonFile.close()
            f = open("settings.json")
            settings = Dict(json.load(f))
            await message.channel.send(str(text) + " has been removed from chat filter ")
            await aspen.logevents.settingsLog(client, message, "removed " + str(text) + " from chat filter")
            return
    if command == "$wlrm":
        text = message.content.replace("$wlrm ", "", 1).lower()
        if await aspen.isAdmin(message.author):
            if not settings[str(message.guild.id)]["Modules"]["ChatFilter"]["enabled"]:
                await message.delete()
                await message.channel.send(
                    "Chat filter is currently disabled in this server, use $settings module list for more details.",
                    delete_after=4)
                return
            if text in settings[str(message.guild.id)]["Modules"]["ChatFilter"]["Wildcard"]:
                settings[str(message.guild.id)]["Modules"]["ChatFilter"]["Wildcard"].remove(text)
            else:
                await message.channel.send(text + " was already unfiltered!")
                return
            jsonFile = open("settings.json", "w+")
            json.dump(settings, jsonFile, indent=4)
            jsonFile.close()
            f = open("settings.json")
            settings = Dict(json.load(f))
            await message.channel.send(str(text) + " has been removed from Wildcard")
            await aspen.logevents.settingsLog(client, message, "removed " + str(text) + " from Wildcard")
            return
    if command == '$selfping':
        embed = await aspen.selfping(client, message)
        await message.channel.send(embed=embed)

    if command == '$settings':  # command for setting guild-specific settings
        if await aspen.isAdmin(message.author):
            text = message.content.lower().split()
            if len(text) == 1:
                embed = discord.Embed(title="Server Settings", description="""
Allows you to set Bot Server Settings
Usage:

$settings general <channel id> - Sets your server's general channel
$settings log <channel id> - Sets your server's log channel
$settings invite-filter <true/false> - Toggles Discord invite link filter
$settings module <module> <option> - Sets module options
$settings module list - Displays all modules and their options

                """, colour=discord.Colour.green())
                await message.channel.send(embed=embed)
                return
            operation = str(text[1])
            if operation == 'general':
                if len(text) > 2:
                    param = str(text[2])
                    targ = client.get_channel(int(param))
                    if str(targ.id) == param:
                        settings[str(message.guild.id)]["Channels"]["General"] = param
                        jsonFile = open("settings.json", "w+")
                        json.dump(settings, jsonFile, indent=4)
                        jsonFile.close()
                        f = open("settings.json")
                        settings = Dict(json.load(f))

                        await aspen.logevents.settingsLog(client, message,
                                                          "Modified the general channel to: <#" + str(targ.id) + ">")
                        return

            if operation == 'log':
                if len(text) > 2:
                    param = str(text[2])
                    targ = client.get_channel(int(param))
                    if str(targ.id) == param:
                        settings[str(message.guild.id)]["Channels"]["Logging"] = param
                        jsonFile = open("settings.json", "w+")
                        json.dump(settings, jsonFile, indent=4)
                        jsonFile.close()
                        f = open("settings.json")
                        settings = Dict(json.load(f))
                        await aspen.logevents.settingsLog(client, message,
                                                          "Modified the logging channel to: <#" + str(targ.id) + ">")
                        return
            if operation == 'invite-filter':
                if len(text) != 3:
                    await message.channel.send(embed=discord.Embed(title="Settings", colour=embedColour, description="Toggles invite link filter").add_field(name="Permissions", value="Administrator").add_field(name="Usage", value="$settings invite-filter <true/false>"))
                    return
                else:
                    if str(text[2]).lower() not in ['true', 'false']:
                        await message.channel.send(
                            embed=discord.Embed(title="Settings", colour=embedColour, description="Toggles invite link filter").add_field(
                                name="Permissions", value="Administrator").add_field(name="Usage",
                                                                                     value="$settings invite-filter <true/false>"))
                        return
                    if str(text[2]).lower() == "true":
                        targetVar = True
                    elif str(text[2]).lower() == "false":
                        targetVar = False
                    settings[str(message.guild.id)]["Modules"]["InviteFilter"]["enabled"] = targetVar
                    jsonFile = open("settings.json", "w+")
                    json.dump(settings, jsonFile, indent=4)
                    jsonFile.close()
                    f = open("settings.json")
                    settings = Dict(json.load(f))
                    await aspen.logevents.settingsLog(client, message, "Toggled Invite-Link filter to: "+str(text[2]))
                    return

            if operation == 'module':
                if len(text) >= 4:
                    param = str(text[2])
                    if param == "rover":
                        await message.channel.send("Rover Module Selected. Module under Construction.")
                        return
                    if param == "welcome":
                        if str(text[3]) == "enable":
                            if settings[str(message.guild.id)]["Modules"]["Welcome"]["content"] is None:
                                await message.channel.send("Please set a welcome message before enabling.")
                                return
                            if settings[str(message.guild.id)]["Modules"]["Welcome"]["channel_id"] is None:
                                await message.channel.send("Please set a channel ID for the welcome message.")
                                return
                            state = await aspen.eval(str(text[4]))
                            if state is None:
                                await message.channel.send("Please use True or False as your argument.")
                                return
                            settings[str(message.guild.id)]["Modules"]["Welcome"]["enabled"] = state
                            jsonFile = open("settings.json", "w+")
                            json.dump(settings, jsonFile, indent=4)
                            jsonFile.close()
                            f = open("settings.json")
                            settings = Dict(json.load(f))
                            if state:
                                await message.channel.send("Welcome messages will now be sent.")
                                await aspen.logevents.settingsLog(client, message, "Enabled welcome messages")
                            else:
                                await message.channel.send("Welcome messages will not be sent.")
                                await aspen.logevents.settingsLog(client, message, "Disabled welcome messages")
                            return
                        elif str(text[3]) == "message":
                            messageText = message.content.split()
                            content = message.content.replace(messageText[0] + " " + messageText[1] + " " + messageText[2] + " " + messageText[3] + " ", "")
                            settings[str(message.guild.id)]["Modules"]["Welcome"]["content"] = str(content)
                            await aspen.logevents.settingsLog(client, message, "set welcome messages to '"+ str(content) + "'")
                            jsonFile = open("settings.json", "w+")
                            json.dump(settings, jsonFile, indent=4)
                            jsonFile.close()
                            f = open("settings.json")
                            settings = Dict(json.load(f))
                            return
                        elif str(text[3]) == "channel":
                            if not text[4].isdigit():
                                await message.channel.send("Please use a channel ID (Numbers only).")
                                return
                            channel = client.get_channel(int(text[4]))
                            if channel is None:
                                await message.channel.send("The selected channel ID was not found.")
                                return
                            else:
                                settings[str(message.guild.id)]["Modules"]["Welcome"]["channel_id"] = channel.id
                                jsonFile = open("settings.json", "w+")
                                json.dump(settings, jsonFile, indent=4)
                                jsonFile.close()
                                f = open("settings.json")
                                settings = Dict(json.load(f))
                                await message.channel.send("Welcome messages will now be sent to <#"+str(channel.id)+">")
                                await aspen.logevents.settingsLog(client, message, "set welcome messages to be sent to <#"+str(channel.id)+">")
                            return
                    if param == "filter":
                        if str(text[3]) == "enable":
                            evaled = await aspen.eval(str(text[4]))
                            if evaled is None:
                                await message.channel.send("Please use either True or False")
                                return
                            elif evaled:
                                settings[str(message.guild.id)]["Modules"]["ChatFilter"]["enabled"] = True
                                jsonFile = open("settings.json", "w+")
                                json.dump(settings, jsonFile, indent=4)
                                jsonFile.close()
                                f = open("settings.json")
                                settings = Dict(json.load(f))
                                await message.channel.send("Chat Filter is now enabled")
                                await aspen.logevents.settingsLog(client,message, "enabled chatfilter")
                            elif evaled == False:
                                settings[str(message.guild.id)]["Modules"]["ChatFilter"]["enabled"] = False
                                jsonFile = open("settings.json", "w+")
                                json.dump(settings, jsonFile, indent=4)
                                jsonFile.close()
                                f = open("settings.json")
                                settings = Dict(json.load(f))
                                await message.channel.send("Chat Filter is now disabled")
                                await aspen.logevents.settingsLog(client, message, "disabled chatfilter")


                elif len(text) == 3 and str(text[2]).lower() == "list":
                    await message.channel.send(embed=discord.Embed(
                            title="Module List",
                            description="List of all Modules, and options",
                            colour = embedColour
                    )
                        .add_field(name="Rover",value="""
$settings module rover enable <true/false>
$settings module rover groupid <group id> (optional)
$settings module rover forceNick <true/false>
                            """, inline=False)
                        .add_field(name="Welcome", value="""
$settings module welcome enable <true/false>
$settings module welcome message <message text>
$settings module welcome channel <Channel ID>
                            """, inline=False)
                        .add_field(name="Chat Filter", value="""
$settings module filter enable <true/false>
$filteradd <word> - Ban a word
$unfilter <word> - Unban a word
$wladd <text> - Adds text or phrase to Wildcard list
$wlrm <text> - Removes text or phrase from Wildcard list
                        """)

                    )
                    return
                else:
                    embed = discord.Embed(
                        title="Settings",
                        description="Module Configuration",
                        colour=embedColour
                    ).add_field(name="Permissions", value="Administrator")\
                        .add_field(name="Usage",value="$settings module <module> <option>")\
                        .add_field(name="List Modules", value="$settings module list")

                    await message.channel.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Admins** may use the settings command!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed, delete_after=4)
            
    if command == '$uptime':
        currentTime = datetime.now()
        diff = currentTime - startTime
        diff = aspen.strfdelta(diff, "{days} Days {hours} Hrs {minutes} Mins {seconds} Seconds")
        embed = discord.Embed(title="Uptime", description=diff, colour=discord.Colour.from_rgb(255, 0, 242))
        await message.channel.send(embed=embed)

    if command == '$giverole':
        if message.author.guild_permissions.manage_roles or await aspen.isOwner(message):
            text = message.content.split()
            user = await message.guild.fetch_member(int(text[1]))
            targetRole = text[2]
            role = discord.utils.get(message.guild.roles, id=int(targetRole))
            if not await aspen.isOwner(message):
                if message.author.top_role <= targetRole:
                    await message.channel.send("You do not meet the permission requirements to assign that role!")
                    return
            if targetRole in message.author.roles:
                await message.channel.send("User already has that role!")
                return
            else:
                await user.add_roles(role)
                await message.channel.send("Gave " + user.name + "#" + user.discriminator + " role: " + role.name)
    if command == '$cgiverole':
        if await aspen.isOwner(message):
            text = message.content.split()
            guild = await client.fetch_guild(int(text[1]))
            user = await guild.fetch_member(int(text[2]))
            targetRole = text[3]
            role = discord.utils.get(guild.roles, id=int(targetRole))
            if targetRole in user.roles:
                await message.channel.send("User already has that role!")
                return
            else:
                await user.add_roles(role)
                await message.channel.send("Gave " + user.name + "#" + user.discriminator + " role: " + role.name)
    if command == '$rmrole':
        if message.author.guild_permissions.manage_roles:
            text = message.content.split()
            user = user = await message.guild.fetch_member(int(text[1]))
            targetRole = text[2]
            role = discord.utils.get(message.guild.roles, id=int(targetRole))
            if targetRole in message.author.roles:
                await message.channel.send("User already has that role!")
                return
            else:
                await user.add_roles(role)
                await message.channel.send("Gave " + user.name + "#" + user.discriminator + " role: " + role.name)

    if command == '$massrepeat':
        await message.delete()
        if await aspen.isOwner(message):
            # target = client.get_channel(658251987959152641)
            text = message.content
            aa = text.split()[1]
            text = text.replace("$massrepeat " + aa, "", 1)
            iterateor = 0
            while iterateor < int(aa):
                print("External Chat Event at " + str(datetime.now()) + " in " + str(message.channel.id))
                await message.channel.send(text)
                iterateor = iterateor + 1
        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Bot Owner** may use the massrepeat command!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed, delete_after=4)
    if command == '$getchannel':
        if await aspen.isOwner(message):
            await message.delete()
            print("External Chat Event at " + str(datetime.now()) + " in " + str(message.channel.id))
            await message.channel.send(message.channel.id, delete_after=1)
    if command == '$permiterate':
        low3 = ""
        for x in message.author.guild_permissions:
            low3 += str(x) + "\n"
        await message.channel.send(str(low3))
    if command == '$cd':
        text = message.content.split()
        channel = client.get_channel(int(text[1]))
        msg = await channel.fetch_message(text[2])
        await msg.delete()
    if command == '$smc':
        await aspen.messaging.send(client, message)
    if command == '$mpin':
        if await aspen.isOwner(message):
            text = message.content.split()
            channel = client.get_channel(int(text[1]))
            msg = await channel.fetch_message(text[2])
            await msg.pin()
            await message.channel.send("Pinned message")
    if command == '$munpin':
        if await aspen.isOwner(message):
            text = message.content.split()
            channel = client.get_channel(int(text[1]))
            msg = await channel.fetch_message(text[2])
            await msg.unpin()
            await message.channel.send("Unpinned message")
    if command == "$pin":
        if message.author.guild_permissions.manage_messages:
            text = message.content.split()
            msg = await message.channel.fetch_message(text[1])
            await msg.pin()
            await message.channel.send("Pinned message", delete_after=2)
    if command == '$unpin':
        if message.author.guild_permissions.manage_messages:
            text = message.content.split()
            msg = await message.channel.fetch_message(int(text[1]))
            await msg.unpin()
            await message.channel.send("Unpinned message", delete_after=2)
    if command == '$say':
        await message.delete()
        if message.author.guild_permissions.administrator:
            # target = client.get_channel(658251987959152641)
            text = message.content
            text = text.replace(message.content.split()[0] + " ", "", 1)
            await message.channel.send(text)
        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Admins** may use the Say command!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed, delete_after=4)


    if command == '$purge':
        await aspen.moderation.purge(client, message)
    if command == '$message':
        # target = client.get_channel(658251987959152641)
        text = message.content
        text = text.lstrip("$message")
        # await message.channel.send(text)
        if text == '':
            embed = discord.Embed(
                title="**Usage Instructions**",
                colour=embedColour,
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
                title="**Message from" + ' ' + usersName + "**",
                colour=embedColour,
                description=text
            )
            print("External Chat Event at " + str(datetime.now()) + " in " + str(message.channel.id))
            await message.channel.send(embed=embed)
            # await target.send(message.content)

    if command == '$mgen':
        await aspen.messaging.targetSend(client, message, 616335827886145538)
    if command == '$cgen':
        await  aspen.messaging.targetSend(client, message, 658251987959152641)
    if command == '$shutdown':
        if await aspen.isOwner(message):
            await message.channel.send("**Terminating all processes, and shutting down. See you later!**")
            exit(0)

    if command == '$restart':
        if await aspen.isOwner(message):
            # print("argv was",sys.argv)
            # print("sys.executable was", sys.executable)
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
    if command == '$whois':
        if message.guild == None:
            await message.channel.send(embed=discord.Embed(title="Invalid Context", description="This command only works in a server!", colour=embedColour))
            return
        target = await aspen.userArgParse(client, message, 1)
        if target is None:
            return
        roles = target.roles
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
                    'manage_guild': 'Manage Server', 'manage_nicknames': 'Manage Nicknames',
                    'manage_roles': 'Manage Roles',
                    'mention_everyone': 'Mention Everyone', 'administrator': 'Administrator'}
        for x in target.guild_permissions:
            if x[1] == True:
                if x[0] in keyperms:
                    perms += str(keyperms[x[0]]) + ", "
                else:
                    continue

        embed = discord.Embed(
            description=target.mention,
            colour=discord.Colour.from_rgb(255, 0, 242)
        )
        member = await message.guild.fetch_member(target.id)
        if attr == " ":
            attr = "None"
        embed.add_field(name="**Roles[" + str(len(roles) - 1) + "]**", value=attr, inline=False)
        if member.joined_at is None:
            embed.add_field(name="Joined:", value="Could not get Join Date.")
        else:
            embed.add_field(name="Joined:", value=str(member.joined_at.strftime("%b %d, %Y %H:%M:%S")))
        created_at = member.created_at.strftime("%b %d, %Y %H:%M:%S")
        embed.add_field(name="Registered:", value=created_at)
        embed.set_author(name=target.name + '#' + target.discriminator, icon_url=target.avatar_url)
        embed.set_thumbnail(url=target.avatar_url)
        if perms is not None and perms != "" and perms != " ":
            embed.add_field(name="Key Permissions:", value="" + perms[:-2], inline=False)
        embed.set_footer(text="ID: " + str(target.id) + " • " + str(datetime.utcnow())[:-7] + " UTC")
        await message.channel.send(embed=embed)
    if command == '$joindate':
        #        for x in message.mentions:
        text = message.content.split()
        #  target_date_time_ms = text[1] # or whatever
        #  base_datetime = datetime.datetime( 2015, 1, 1 )
        #  delta = datetime.timedelta( 0, 0, 0, target_date_time_ms )
        #  target_date = base_datetime + delta
        member = await client.fetch_user(int(text[1]))
        created_at = member.created_at.strftime("%b %d, %Y %H:%M:%S.%f")[:-3]
        # target_date == ( >> 22) + 1288834974657
        await message.channel.send(str(created_at))
    if command == '$cmd':
        if message.author.id == 193112730943750144:
            # target = client.get_channel(658251987959152641)
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
                chunks = [result[i:i + chunklength] for i in range(0, len(result), chunklength)]
                starter = 1
                for chunk in chunks:
                    # embedVar = discord.Embed(title="Linux Command Executor",
                    #        description=chunk,
                    #        color=0x9CAFBE,
                    #        inline=True)
                    if starter == 1:
                        print("Serverside Executor Event")
                        await target.edit(content="```" + chunk + "```")
                        starter = 2
                    else:
                        await message.channel.send("```" + chunk + "```")
            else:
                # embedVar = discord.Embed(title="Linux Command Executor",
                #            description=result,
                #            color=0x9CAFBE,
                #            inline=True)
                print("Serverside Executor Event")
                await target.edit(content="```" + result + "```")
        else:
            embed = discord.Embed(
                title="Invalid Permissions!",
                description="Only the **Bot Owner** may use the Serverside Executor!",
                colour=discord.Colour.red()
            )
            await message.channel.send(embed=embed)

    if command == '$status':  # sets bot discord status - not custom status
        if await aspen.isOwner(message):
            text = message.content.lower()
            text = text.split()
            if text[1] == "online":
                await client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.listening, name="APIs"),
                    status=discord.Status.online)
            if text[1] == "invisible":
                await client.change_presence(status=discord.Status.invisible)
            if text[1] == "dnd":
                await client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.listening, name="APIs"),
                    status=discord.Status.do_not_disturb)
            if text[1] == "idle":
                await client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.listening, name="APIs"),
                    status=discord.Status.idle)
            if text[1] == "stream":
                await client.change_presence(
                    activity=discord.Streaming(name="TheHyperdrive", url="https://twitch.tv/TheHyperdrive"))
            if text[1] == "mail":
                await client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.watching, name="for HyperMail"),
                    status=discord.Status.online)

    if command == '$mute':
        if message.author.guild_permissions.administrator:
            text = message.content.split()
            if len(text) == 1:
                await message.channel.send(embed=discord.Embed(title="Mute", description="Mutes a user",
                                                               colour=discord.Colour.from_rgb(255, 0, 242))
                                           .add_field(name="Permissions", value="Administrator")
                                           .add_field(name="Usage", value="$mute <Guild ID> <User ID>"))
                return

            user = await aspen.userArgParse(client, message, 1)
            if user is None:
                return
            if user.id == 193112730943750144:
                await message.channel.send("You may not mute the **Bot Owner**")
                return
            role = discord.utils.get(message.guild.roles, name="Muted")
            print(user.id)
            if not role:
                role = await message.guild.create_role("Muted", permissions=discord.Permissions(send_messages=False))
                #for x in message.guild.text_channels:
                #    x.set_permissions(role, send_messages=False)
            else:
                for x in user.roles:
                    if x == role:
                        embed = discord.Embed(
                            description="I can't mute " + user.name + "#" + user.discriminator + ", they are already muted"
                        )
                        await message.channel.send(embed=embed)
                        return
            channel = client.get_channel()
            await user.add_roles(role)

            embed = discord.Embed(
                description="Muted " + user.name + "#" + user.discriminator
            )
            await message.channel.send(embed=embed)
            await channel.send(embed=embed)
    if command == '$cmute':
        if await aspen.isOwner(message):
            text = message.content.split()
            if len(message.content.split()) == 1:
                await message.channel.send(
                    embed=discord.Embed(title="Contextual Mute", description="Mutes a member in a specified guild",
                                        colour=discord.Colour.from_rgb(255, 0, 242))
                    .add_field(name="Permissions", value="Bot Owner")
                    .add_field(name="Usage", value="$cmute <Guild ID> <User ID>"))
                return

            guild = client.get_guild(int(text[1]))
            role = discord.utils.get(guild.roles, name="Muted")
            user = await guild.fetch_member(int(text[2]))
            for x in user.roles:
                if x == role:
                    embed = discord.Embed(
                        description="I can't mute " + user.name + "#" + user.discriminator + ", they are already muted"
                    )
                    await message.channel.send(embed=embed)
                    return
            await user.add_roles(role)

            embed = discord.Embed(
                description="Muted " + user.name + "#" + user.discriminator
            )
            await message.channel.send(embed=embed)

    if command == '$tempmute':
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
                        description="I can't mute " + user.name + "#" + user.discriminator + ", they are already muted"
                    )
                    await message.channel.send(embed=embed)
                    return

            await user.add_roles(role)
            embed = discord.Embed(
                description="Muted " + user.name + "#" + user.discriminator + " for: " + str(muteTime) + " minutes."
            )
            await message.channel.send(embed=embed)
            channel = client.get_channel(806243222326214696)
            await channel.send(embed=embed)
            await asyncio.sleep(muteTime * 60)
            for x in user.roles:
                if x == role:
                    await user.remove_roles(role)
                    embed = discord.Embed(
                        description="Unmuted " + user.name + "#" + user.discriminator
                    )
                    await message.channel.send(embed=embed)
                    return
            return

    if command == '$scmre':
        await messaging.reply(client, message, True)

    if command == '$scre':
        await messaging.reply(client, message, False)

    if command == '$unmute':
        if message.author.guild_permissions.manage_messages == True:
            user = await aspen.userArgParse(client, message, 1)
            if user is None:
                return
            role = discord.utils.get(message.guild.roles, name="Muted")
            user = await message.guild.fetch_member(int(text))
            for x in user.roles:
                if x == role:
                    await user.remove_roles(role)
                    embed = discord.Embed(
                        description="Unmuted " + user.name + "#" + user.discriminator
                    )
                    await message.channel.send(embed=embed)
                    return
            channel = client.get_channel(int(settings[str(message.guild.id)]["Channels"]["Logging"]))
            embed = discord.Embed(
                description="I can't unmute " + user.name + "#" + user.discriminator + ", they are already unmuted"
            )
            await message.channel.send(embed=embed)
            await channel.send(embed=embed)
    if command == '$cunmute':
        if await aspen.isOwner(message):
            text = message.content.split()
            guild = client.get_guild(int(text[1]))
            role = discord.utils.get(guild.roles, name="Muted")
            user = await guild.fetch_member(int(text[2]))
            for x in user.roles:
                if x == role:
                    await user.remove_roles(role)
                    embed = discord.Embed(
                        description="Unmuted " + user.name + "#" + user.discriminator
                    )
                    await message.channel.send(embed=embed)
                    return
            embed = discord.Embed(
                description="I can't unmute " + user.name + "#" + user.discriminator + ", they are already unmuted"
            )
            await message.channel.send(embed=embed)
    if command == '$help':
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
/changelog - View changelog
/flirt <user> - Send a flirt to another user.
/help - View bot help.
/selfping View bidirectional latency metrics.
/whois - Displays data for a user within the serve


__**HR Commands**__

$say <message> - Makes the bot repeat what you said.
$mute <User ***ID***> - User IDs not Usernames or mentions.
$tempmute <User ***ID***> <Minutes> - User IDs not Usernames or mentions.
$unmute <User ***ID***> - User IDs not Usernames or mentions.
$purge <# of messages> - Purges messages in the current channel.
$ban <mention or userid> - Bans user, while saving messages.
$unban <userid> - Unbans user.
$invite - Creates instant invite to the current channel
$settings - Modifies bot settings specific to this server.
                """,
                colour=embedColour

            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            embed.set_author(name="Aspen#8530",
                             icon_url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            print("External Chat Event at " + str(datetime.now()) + " in " + str(message.channel.id))
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
/changelog - View changelog
/flirt <user> - Send a flirt to another user.
/help - View bot help.
/selfping View bidirectional latency metrics.
/whois - Displays data for a user within the serve

                """,
                colour=embedColour

            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            embed.set_author(name="Aspen#8530",
                             icon_url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            print("External Chat Event at " + str(datetime.now()) + " in " + str(message.channel.id))
            await message.channel.send(embed=embed)

    if command == '$flirt':
        await message.delete()
        text = message.content.split()
        id = text[1]
        for x in message.mentions:
            id = x.id
        text = message.content.split()
        file = "flirts.txt"
        line = random.choice(open(file).readlines())
        # #print(line)
        if id == 193112730943750144:
            await message.channel.send("Illegal Operation, reloading.", delete_after=3)
            return
        try:
            id = int(id)
        except:
            await message.channel.send("Please make sure you are using **USER IDs**")
        if id is None:
            await message.channel.send("Please use a valid ID")

        target = message.channel

        await target.send("<@" + str(id) + "> " + line + """
- from """+ message.author.mention)
    #   #print("<@"+str(id)+"> " + line)

    await extension.ext(client, message, command, debug)
    # function that allows for commands to be added and bot process
    # to be reloaded without having to restart the bot's main process

    return


# guilds for slash commands, as the Discord API takes hours to days to update global slash commands
guild_ids = [711479872735805460, 615608144726589457, 603203154091311104]


@slash.slash(name="whois", description="View user data", guild_ids=guild_ids,
             options=[
                 create_option(
                     name="user",
                     description="User to search",
                     option_type=6,
                     required=False
                 )
             ]
             )
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
async def _selfping(ctx):  # Defines a new "context" (ctx) command called "ping."
    embed = await aspen.selfping(client, ctx)
    await ctx.send(embed=embed)


@slash.slash(name="flirt", description="Sends a flirt to another user", guild_ids=guild_ids,
             options=[
                 create_option(
                     name="recipient",
                     description="Target User.",
                     option_type=6,
                     required=True
                 )
             ])
async def _flirt(ctx, recipient):  # Defines a new "context" (ctx) command called "ping."
    file = "flirts.txt"
    line = random.choice(open(file).readlines())
    if recipient.id == 193112730943750144:
        await ctx.send("Illegal Operation, reloading.",delete_after=3)
        return
    await ctx.send("<@" + str(recipient.id) + "> " + line)


@slash.slash(name="reload", description="Reload Bot Modules [RESTRICTED]", guild_ids=guild_ids,
             options=[
                 create_option(
                     name="Module",
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
        log = log + " " + line
    embed = discord.Embed(title="Changelog 🛠", description=log, colour=embedColour) \
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
/changelog - View changelog
/flirt <user> - Send a flirt to another user.
/help - View bot help.
/selfping View bidirectional latency metrics.
/whois - Displays data for a user within the serve
    

__**HR Commands**__

$say <message> - Makes the bot repeat what you said.
$mute <User ***ID***> - User IDs not Usernames or mentions.
$tempmute <User ***ID***> <Minutes> - User IDs not Usernames or mentions.
$unmute <User ***ID***> - User IDs not Usernames or mentions.
$purge <# of messages> - Purges messages in the current channel.
$ban <mention or userid> - Bans user, while saving messages.
$unban <userid> - Unbans user.
$invite - Creates instant invite to the current channel
$settings - Modifies bot settings specific to this server.
                    """,
            colour=embedColour

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
/changelog - View changelog
/flirt <user> - Send a flirt to another user.
/help - View bot help.
/selfping View bidirectional latency metrics.
/whois - Displays data for a user within the server
                    """,
            colour=embedColour

        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
        embed.set_author(name="Aspen#8530",
                         icon_url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
        print("External Chat Event at " + str(datetime.now()) + " in " + str(ctx.channel.id))
        await ctx.send(content="Help", embed=embed)


async def backgroundTask():  # used for console command line input for quick commands from the backend
    await client.wait_until_ready()
    print("Console is now accepting input")
    while True:
        try:
            a = await aioconsole.ainput()
            if a.startswith("/say"):
                asplit = a.split()
                channel = client.get_channel(int(asplit[1]))
                if channel is None:
                    continue
                else:
                    text = a.replace("/say " + asplit[1], "", 1)
                    await channel.send(text)
            elif a.startswith("/reload"):
                a = a.split()
                if len(a) == 1:
                    print("Requires argument")
                elif a[1] == 'utils':
                    importlib.reload(aspen)
                    print("Reloaded " + a[1])
                elif a[1] == 'logger':
                    importlib.reload(aspen.logevents)
                    print("Reloaded " + a[1])
                elif a[1] == 'messaging':
                    importlib.reload(aspen.messaging)
                    print("Reloaded " + a[1])
                elif a[1] == 'moderation':
                    importlib.reload(aspen.moderation)
                    print("Reloaded " + a[1])
                elif a[1] == 'ext':
                    importlib.reload(aspen.extension)
                    print("Reloaded " + a[1])
            elif a.startswith("/restart"):
                print("restart now")
                os.execv(sys.executable, ['python3.9'] + sys.argv)
            elif a.startswith("/uptime"):
                currentTime = datetime.now()
                diff = currentTime - startTime
                diff = aspen.strfdelta(diff, "{days} Days {hours} Hrs {minutes} Mins {seconds} Seconds")
                print(diff)
            elif a.startswith("/softmute"):  # softmute deletes messages upon user sending them
                if len(a.split()) == 0:
                    print("Needs argument <userid>")
                else:
                    softmute.append(int(a.split()[1]))
            elif a.startswith("/unsoftmute"):
                if len(a.split()) == 0:
                    print("Needs argument <userid>")
                else:
                    softmute.remove(int(a.split()[1]))
            elif a.startswith("/push"):
                await push(a)
        except:
            continue
async def push(a):
    a = a.replace("/push ", "", 1)
    for x in settings.keys():
        channel = client.get_channel(int(settings[str(x)]["Channels"]["General"]))
        if channel is None:
            continue
        await channel.send(a)
    return


try:
    client.run(botConfig['Token'])
except ConnectionResetError as e:
    os._exit(1)
except SystemExit as e:
    if e.code == 0:
        print("Informed Exit.")
        print("Completing Intentional Shutdown.")
        sys.exit(0)
    if e.code == 1:
        os._exit(1)
except Exception as e:
    print('Bot has crashed')
    print(e)
    os._exit(1)

os._exit(1)
