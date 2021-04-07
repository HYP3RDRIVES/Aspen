
from datetime import datetime
import discord
from addict import Dict
import json
import asyncio

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

async def ping(client, message):
    elapsed_time = 0
    msgtime = message.created_at
    now = datetime.utcnow()
    #now - msgtime datetime.timedelta(0, 3, 519319)
    diff = now - msgtime
    elapsed_time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
    elapsed_time = str(elapsed_time)
    frameworklat = str(client.latency*1000)
    embed = discord.Embed(title="Ping",description="Bot Latency",colour=discord.Colour.from_rgb(255, 0, 242))\
        .add_field(name="Serverside", value=elapsed_time+ " ms")\
        .add_field(name="Framework", value=frameworklat[:-11]+" ms")
    print("External Chat Event at "+str(datetime.now())+" in "+str(message.channel.id))
    await message.channel.send(embed=embed)

async def selfping(client, message):
    postTime = datetime.utcnow()
    msg = await message.channel.send("####%--PING$$-"+str(postTime))
    elapsed_time = 0
    uplink_time = 0
    msgtime = msg.created_at
    now = datetime.utcnow()
    #now - msgtime datetime.timedelta(0, 3, 519319)
    diff = now - msgtime
    await msg.delete()
    elapsed_time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
    elapsed_time = str(elapsed_time)
    diff = msgtime-postTime
    uplink_time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
    uplink_time = str(uplink_time)
    frameworklat = str(client.latency*1000)
    print("External Chat Event at "+str(datetime.now())+" in "+str(message.channel.id))
    embed = discord.Embed(title="Ping", description="Self-measured Bot Latency", colour=discord.Colour.from_rgb(255, 0, 242)) \
        .add_field(name="Message Send", value=uplink_time + " ms") \
        .add_field(name="Message Receive", value=elapsed_time + " ms") \
        .add_field(name="Framework", value=frameworklat[:-11] + " ms", inline=False)
    return embed

async def ignoreUser(id, guild, state):
    if state:
        f = open("settings.json")
        settings = Dict(json.load(f))
        settings[str(guild)]["Users"]["Ignored"].setdefault(id,)
        jsonFile = open("settings.json", "w+")
        json.dump(settings, jsonFile, indent=4,)
        jsonFile.close()
    else:
        file = open("settings.json")
        settings = Dict(json.load(file))
        settings[str(guild)]["Users"]["Ignored"].pop(id)
        jsonFile = open("settings.json", "w+")
        json.dump(settings, jsonFile, indent=4, )
        jsonFile.close()
async def getChannel(client, message, type):
    f = open("settings.json")
    settings = Dict(json.load(f))
    channelid = settings[str(message.guild.id)]["Channels"][type]
    channel = client.get_channel(int(channelid))
    return channel



