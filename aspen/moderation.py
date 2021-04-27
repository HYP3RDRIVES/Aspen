import aspen
import discord
from aspen import logevents

async def purge(client, message):
    if message.author.guild_permissions.administrator == True or aspen.isOwner(message):
        text = message.content.split()
        if len(text) != 2:
            await message.channel.send(embed=discord.Embed(title="Purge", description="Purges messages from the channel",
                                                               colour=discord.Colour.from_rgb(255, 0, 242))
                                           .add_field(name="Permissions", value="Administrator")
                                           .add_field(name="Usage", value="$purge <# of messages>"))
        await message.delete()
        await message.channel.purge(limit=int(text[1]))
        stringy = text+" Messages deleted in <#"+str(message.channel.id)+">"
        await logevents.internalEventLog(client, message.guild.id, message.author, "Purge", stringy)

async def delete(client, message):
    if message.author.guild_permissions.administrator or aspen.isOwner(message):
        text = message.content.split()
        ctx = text[1]
        target = text[2]
        ctx = client.get_channel(int(ctx))
        msg = ctx.fetch_message(int(target))
        await msg.delete()
        return

async def warn(client, message):
    return

