import discord
from addict import Dict
import json
from datetime import datetime
import subprocess
import aspen
embedColour = discord.Colour.from_rgb(255, 0, 242)

try:
    f = open("settings.json")
    settings = Dict(json.load(f))
except:
    print("An error has occurred")

async def permError(client, message, permission):
    embed = discord.Embed(title="Insufficient Permissions", description="Only "+permission+" is allowed to run this command!", colour=discord.Colour.red())
    await message.channel.send(embed=embed)
async def filterLog(client, message, key):
    embed = discord.Embed(
        title="Global Filter",
        description="Banned word triggered by `Wildcard`",
        colour=discord.Colour.from_rgb(255, 0, 242)
    )
    embed.add_field(name="Banned Word", value=key)
    embed.add_field(name="Full Message", value=message.content, inline=False)
    embed.set_author(name=message.author.name + '#' + message.author.discriminator, icon_url=message.author.avatar_url)
    channel = await aspen.getChannel(client, message, "Logging")
    print("Internal Chat Event at " + str(datetime.now()) + " in " + str(channel.id))
    await channel.send(embed=embed)
    return
async def internalEventLog(client, guild, user, action, string=None):
    f = open("settings.json")
    settings = Dict(json.load(f))
    if string is None:
        string = "\u200b"
    embed = discord.Embed(title=action,description=string, colour=embedColour)
    embed.set_author(name=user.name+"#"+user.discriminator, icon_url=user.avatar_url)
    channelid = settings[str(guild)]["Channels"]["Logging"]
    channel = client.get_channel(int(channelid))
    await channel.send(embed=embed)
    return
async def deleteLog(client, message):
    if message.author == client.user:
        return

    f = open("settings.json")
    settings = Dict(json.load(f))
    embed = discord.Embed(colour=discord.Colour.red(), description=str(message.content))
    try:
        targetLoc = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+"_"+message.attachments[0].filename
        action = "sudo wget "+message.attachments[0].proxy_url+" -O /var/www/file-share/1/discord-del/"+targetLoc
        print(subprocess.check_output(action, shell=True))
        imagePresent = True

    except:
        imagePresent = False
    if imagePresent == True:

        embed.set_image(url="https://deleted.hypr.ax/"+targetLoc)
        embed.add_field(name="Location", value="[File](https://deleted.hypr.ax/" + targetLoc, inline=False)
        # print(targetLoc)

    embed.add_field(name="\u200b", value="**Message sent by <@"+str(message.author.id)+"> deleted in <#"+str(message.channel.id)+">**")
    embed.set_author(name=message.author.name+'#'+message.author.discriminator, icon_url=message.author.avatar_url)
    embed.set_footer(text="Author ID: "+str(message.author.id)+" Message ID: "+str(message.id)+" Timestamp: "+str(datetime.utcnow()))
    channel = settings[str(message.guild.id)]["Channels"]["Logging"]
    await client.get_channel(int(channel)).send(embed=embed)

async def settingsLog(client, message, action):
    user = message.author
    guild = message.guild.id
    f = open("settings.json")
    settings = Dict(json.load(f))
    embed = discord.Embed(
        title="Settings Modification",
        description=user.mention+" has "+action,
        colour=discord.Colour.green()
    )
    embed.set_author(name=user.name+"#"+user.discriminator, icon_url=user.avatar_url)
    channel = settings[str(guild)]["Channels"]["Logging"]
    await client.get_channel(int(channel)).send(embed=embed)
    return