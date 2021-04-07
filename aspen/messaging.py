
async def reply(client, message, mentionable):
    if message.author.guild_permissions.administrator == True:
        text = message.content.split()
        messageid = text[2]
        channel = client.get_channel(int(text[1]))
        msg = await channel.fetch_message(int(messageid))
        textTarg = str(text[0]+" "+text[1]+" "+text[2])
        text = message.content.replace(textTarg, "", 1)
        await channel.send(content=text, reference=msg, mention_author=mentionable)
        return

async def send(client, message):
    await message.delete()
    if message.author.guild_permissions.administrator == True:
        text = message.content.split()
        channel = client.get_channel(int(text[1]))
        textTarg = str(text[0]+" "+text[1])
        text = message.content.replace(textTarg, "", 1)
        await channel.send(text)
        return
async def targetSend(client, message, channelid):
    if message.author.guild_permissions.administrator == True:
        text = message.content
        text = text.replace(message.content.split()[0]+" ", "", 1)
        channel = client.get_channel(channelid)
        await message.delete()
        await channel.send(text)
        return