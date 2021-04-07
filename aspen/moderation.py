from aspen import logevents

async def purge(client, message):
    if message.author.guild_permissions.administrator == True:
        text = message.content
        text = text.replace("$purge ", "", 1)
        await message.delete()
        await message.channel.purge(limit=int(text))
        stringy = text+" Messages deleted in <#"+str(message.channel.id)+">"
        await logevents.internalEventLog(client, message.guild.id, message.author, "Purge", stringy)

async def delete(client, message):
    if message.author.guild_permissions.administrator:
        text = message.content.split()
        ctx = text[1]
        target = text[2]
        ctx = client.get_channel(int(ctx))
        msg = ctx.fetch_message(int(target))
        await msg.delete()
        return

async def warn(client, message):
    return

async def mute(client, message):
    return
