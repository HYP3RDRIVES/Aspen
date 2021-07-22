import discord
import aspen
from aspen import  moderation, logevents
from datetime import datetime
import resource
import requests
import asyncio
import xmltodict
import json
from addict import Dict
embedColour = discord.Colour.from_rgb(255, 0, 242)

async def init(client, message, command, debugstate):


    if message.author == client.user:
        return
    if message.author.bot:
        return

    if command == "!call" and message.guild.id == 735872336045277234:
        await client.get_channel(758729070111490109).send("@everyone Call from: "+message.author.name+"#"+message.author.discriminator+" at "+str(message.jump_url))
        await message.channel.send("Moderator call. Please standby.")
    for x in message.mentions:
        if x == client.user:
            embed = discord.Embed(
                title="Aspen#8530",
                description="""A bot developed and maintained by <@193112730943750144>

    Currently running **Aspen v1.1.2**

                        """
            )
            embed.set_footer(text="Message will delete after 30 seconds")
            #if message.guild != None:
            #    embed.add_field(name="Shard ID", value=str(message.guild.shard_id))
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            # print("Internal Chat Event at " + str(datetime.now()) + " in " + str(message.channel.id))
            await message.channel.send(embed=embed, delete_after=30)
    return


async def ext(client, message, command, debugstate):
    text = message.content.split()
    if "--debug" in message.content:
        await message.channel.send("Extensions Command: "+command)

    if command == "$av":
        if len(text) == 2:
            if text[1] == "help":
                await message.channel.send(
                embed=discord.Embed(title="Avatar", description="Displays the Avatar of a selected user",
                                    colour=discord.Colour.from_rgb(255, 0, 242))
                .add_field(name="Permissions", value="Everyone")
                .add_field(name="Usage", value="$av <User>"))
                return
        target = await aspen.userArgParse(client,  message, 1)
        if target is None:
            return
        avatar_loc = target.avatar_url
        embed = discord.Embed(title="Avatar for " + target.name + "#" + target.discriminator,
                              colour=discord.Colour.from_rgb(255, 0, 242))
        embed.set_image(url=avatar_loc)
        embed.set_author(name=message.author.name + "#" + message.author.discriminator,
                         icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    if command == "$s":
        if message.author.id == 193112730943750144:
            text = message.content.split()
            if len(text) != 2:
                await message.channel.send("Invalid syntax")
                return
            r = requests.post("https://s.hypr.ax/shorten/"+text[1], headers={"Authorization":"DeyhX6AFpkV7uL93L4u6dCyaSbiyfFB4iQmLvhkx"})
            if r.status_code == 200:
                await message.channel.send(r.text)
            else:
                await message.channel.send("Invalid URL")
                return
    if command == "$invite":
        if message.author.guild_permissions.administrator == True:
            link = await message.channel.create_invite(max_age=300)
            await message.channel.send("Here is an instant invite to your server: " + str(link))
    if command == '$cdel':
        text = message.content.split()
        await message.delete()
        if message.author.id != 193112730943750144:
            return
        channel = client.get_channel(text[1])
        msg = channel.fetch_message(text[2])
        await msg.delete()
    if command == '$info':
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000
        await message.channel.send(str(usage/1000))
    if message.content.startswith('$changelog'):
        file1 = open("changelog.txt")
        log = ""
        for line in file1:
            log = log+" "+line
        embed = discord.Embed(title="Changelog 🛠", description=log, colour=discord.Colour.from_rgb(255,0,242))\
            .set_footer(text="Use $help for commands")
        await message.channel.send(embed=embed)

    if command == '$ban':
        if message.author.guild_permissions.ban_members or await aspen.isOwner(message):
            if len(text) == 1 or (len(text) == 2 and text[1] == "help"):
                await message.channel.send(embed=discord.Embed(title="Ban", description="Bans a member from the Server",
                                                               colour=discord.Colour.from_rgb(255, 0, 242))
                                           .add_field(name="Permissions", value="Ban Members")
                                           .add_field(name="Usage", value="$ban <User>"))
                return "Exit"



            user = await aspen.userArgParse(client,  message, 1)
            if message.guild.get_member(user.id) is not None:
                if not await aspen.isOwner(message):
                    if message.author.top_role <= user.top_role:
                        await message.channel.send("You do not meet the permission requirements to assign that role!")
                        return
            if user is None:
                return "Exit"
            if user.id == client.user.id:
                await message.channel.send("Sorry, I cannot ban myself!")
                return
            if user.id == 193112730943750144 and await aspen.isOwner(message):
                if "--force" in message.content.lower():
                    print("banning bot owner")
                else:
                    await message.channel.send("You may not ban the **Bot Owner**")
                    return "Exit"
            await message.guild.ban(user=user,delete_message_days=0)
            await message.channel.send(
                embed=discord.Embed(title="User Banned!",
                                    description="Banned "+user.name+"#"+user.discriminator,
                                    colour=discord.Colour.red()
                                    )
            )
    if command == "$filterlist":
        if not await aspen.isAdmin(message.author):
            await message.channel.send("This is restricted to **Admins** only!")
            return

        f = open("settings.json")
        settings = Dict(json.load(f))  # loads guild specific settings
        f.close()
        if not settings[str(message.guild.id)]["Modules"]["ChatFilter"]["enabled"]:
            await message.delete()
            await message.channel.send("Chat filter is currently disabled in this server, use $settings module list for more details.", delete_after=4)
            return
        bnText = ""
        wlText = ""
        for x in settings[str(message.guild.id)]["Modules"]["ChatFilter"]["BannedWords"]:
            bnText = bnText + "\n" + str(x)
        for x in settings[str(message.guild.id)]["Modules"]["ChatFilter"]["Wildcard"]:
            wlText = wlText + "\n" + str(x)
        if wlText == "":
            wlText = "No words in list"
        if bnText == "":
            bnText = "No words in list"
        await message.channel.send(embed=discord.Embed(title="Filter List", description="Filtered Words", colour=embedColour)
                                   .add_field(name="Banned Words", value=bnText, inline=False)
                                   .add_field(name="Wildcard", value=wlText, inline=False))
    if command == '$cban':
        if aspen.isOwner(message):
            if "--force" in message.content:
                message.content = message.content.replace("--force", "", 1)
            if len(text) == 1:
                await message.channel.send(embed=discord.Embed(title="Contextual Ban", description="Bans a member from a specified guild",
                                                               colour=discord.Colour.from_rgb(255, 0, 242))
                                           .add_field(name="Permissions", value="Bot Owner")
                                           .add_field(name="Usage", value="$cban <Guild ID> <User ID>"))
                return
            user = await aspen.userArgParse(client,  message, 2)
            if user is None:
                return
            if user.id == 193112730943750144:
                await message.channel.send("You may not ban the **Bot Owner**")
                return
            guild = client.get_guild(int(text[1]))
            await guild.ban(user=user,delete_message_days=0)
            await message.channel.send(embed=discord.Embed(title="User Banned!",description="Banned "+user.name+"#"+user.discriminator,colour=discord.Colour.red()))
    if command == '$cunban':
        if aspen.isOwner(message):
            if len(text) == 1:
                await message.channel.send(embed=discord.Embed(title="Contextual Unan", description="Unans a member from a specified guild",
                                                               colour=discord.Colour.from_rgb(255, 0, 242))
                                           .add_field(name="Permissions", value="Bot Owner")
                                           .add_field(name="Usage", value="$cunban <Guild ID> <User ID>"))
                return
            user = await aspen.userArgParse(client,  message, 2)
            if user is None:
                return
            guild = client.get_guild(int(text[1]))
            await guild.unban(user)
            await message.channel.send(embed=discord.Embed(title="User Unanned!",description="Unanned "+user.name+"#"+user.discriminator))
        else:
            return
    if command == '$unban':
        if message.author.guild_permissions.ban_members:
            if len(text) == 1:
                await message.channel.send(
                    embed=discord.Embed(title="Unban", description="Unbans a user from this guild",
                                        colour=discord.Colour.from_rgb(255, 0, 242))
                    .add_field(name="Permissions", value="Ban Members")
                    .add_field(name="Usage", value="$unban <User ID>"))
                return
            user = await aspen.userArgParse(client,  message, 1)
            if user is None:
                return
            await message.guild.unban(user)
            await message.channel.send("Unbanned "+user.name+"#"+user.discriminator)
            #
            #    await message.channel.send("User either not banned or not found")

    if command == '$test':
        await message.channel.send("done")
    if command == '$echo':
        if aspen.isOwner(message):
            await message.channel.send(message.content)
    if message.author.id == 750835145556230206:
        for x in [":smiling_face_with_3_hearts:", "babe", "🥰"]:
            if x in message.content.lower():
                await message.delete()
    if command == '$cat':
        file = ""
        msg = await message.channel.send("Searching for a cat...")
        try:
            r = requests.get("https://aws.random.cat/meow")
            file = r.json()['file']
        except:
            if r.status_code != 200:
                if debugstate:
                    await msg.edit(content="It seems the image API is having issues right now, try again later. \n HTTP CODE:"+str(r.status_code))
                else:
                    await msg.edit(content="It seems the image API is having issues right now, try again later.")
            else:
                await msg.edit(content="The bot encountered an issue. Please try again later.")
            return
        embed = discord.Embed(title="Found a Cat! 😺", colour=discord.Colour.from_rgb(255,0,242))\
            .set_image(url=file)
        await msg.edit(embed=embed, content="\u2000")
        return "exit"
    if command == '$dog':
        msg = await message.channel.send("Searching for a dog...")
        r = requests.get("https://random.dog/woof.json")
        file = r.json()
        while int(file['fileSizeBytes']) >= 100000:
            #print("gettings")
            r = requests.get("https://random.dog/woof.json")
            file = r.json()
        embed=discord.Embed(title="Found a Dog! 🐕", colour=discord.Colour.from_rgb(255,0,242))\
            .set_image(url=file['url'])
        await msg.edit(embed=embed, content="\u2000")

    if command == '$msend':
        if message.author.id == 193112730943750144 or message.author.id == 373992293071585281:
            print("ok")
        else:
            return
        text = message.content.split()
        await message.delete()
        if len(text) < 3:
            await message.channel.send("Incorrect!", delete_after=1)
        guild = client.get_guild(615608144726589457)
        try:
            user = await guild.fetch_member(int(text[1]))
        except:
            user = await client.fetch_user(int(text[1]))
        if user is None:
            user = await client.fetch_user(int(text[1]))
        if user is None:
            await message.channel.send("Invalid!!", delete_after=1)
        pfp = str(user.avatar_url)
        try:
            username = str(user.nick)
        except:
            username = str(user.name)
        if username == "None":
            username = str(user.name)
        content = message.content.replace(text[0] + " " + text[1], "", 1)

        r = requests.post(
            "https://discord.com/api/webhooks/826588669074210836/uXOx6HCgN8QH3hS2s256-ixYyb7GjBZMTMtEKs0UeSvUu-L_4HU8Ny5HITNcthy6yl89",
            headers={'User-Agent': 'Mozilla/5.0'},
            data={'content': content, 'username': username, 'avatar_url': pfp}
            )

    if command == '$cpurge':
        channel = client.get_channel(int(text[1]))
        await channel.purge(limit=int(text[2]))

    if command == '$msend':
        if aspen.isOwner(message) or message.author.id == 373992293071585281:
            print("ok")
        else:
            return
        text = message.content.split()
        await message.delete()
        if len(text) < 3:
            await message.channel.send("Incorrect!", delete_after=1)
        guild = client.get_guild(615608144726589457)
        try:
            user = await guild.fetch_member(int(text[1]))
        except:
            user = await client.fetch_user(int(text[1]))
        if user is None:
            user = await client.fetch_user(int(text[1]))
        if user is None:
            await message.channel.send("Invalid!!", delete_after=1)
        pfp = str(user.avatar_url)
        try:
            username = str(user.nick)
        except:
            username = str(user.name)
        if username == "None":
            username = str(user.name)
        content = message.content.replace(text[0] + " " + text[1], "", 1)

        r = requests.post(
            "https://discord.com/api/webhooks/826588669074210836/uXOx6HCgN8QH3hS2s256-ixYyb7GjBZMTMtEKs0UeSvUu-L_4HU8Ny5HITNcthy6yl89",
            headers={'User-Agent': 'Mozilla/5.0'},
            data={'content': content, 'username': username, 'avatar_url': pfp}
        )
        # #print(r.text)
    if command == '$timein':
        text = message.content.split()
        if len(text) != 2:
            await message.channel.send(embed=discord.Embed(title=""))
    if command == '$rule34':
        if message.channel.is_nsfw() or message.channel.id == 826098129110564885:
            args = message.content.lower().replace("$rule34", "", 1)
            args = args.replace(" ", "+")
            r = requests.get("https://rule34.xxx/index.php?page=dapi&s=post&limit=10&q=index&tags="+args)
            parsed = xmltodict.parse(r.text)
            result = json.dumps(parsed)
            if parsed["posts"]["@count"] == "0":
                await message.channel.send("No results found!")
                return
            string_length = len(result)
            if string_length > 1900:
                chunklength = 1889
                chunks = [result[i:i + chunklength] for i in range(0, len(result), chunklength)]
                for chunk in chunks:

                    await message.channel.send(chunk)
            else:
                await message.channel.send(content=result)

            # await message.channel.send(r.text)
        else:
            await message.channel.send("This command is only allowed in NSFW channels!")
            return

    if command == '$roleiter':
        if message.author.guild_permissions.manage_roles:
            string_length = len(str(message.guild.roles))
            if string_length > 1900:
                chunklength = 1899
                chunks = [str(message.guild.roles)[i:i + chunklength] for i in range(0, len(str(message.guild.roles)), chunklength)]
                starter = 1
                for chunk in chunks:
                    # embedVar = discord.Embed(title="Linux Command Executor",
                    #        description=chunk,
                    #        color=0x9CAFBE,
                    #        inline=True)
                    if starter == 1:
                        await message.channel.send(content=chunk)
                        starter = 2
                    else:
                        await message.channel.send(chunk)
            else:
                # embedVar = discord.Embed(title="Linux Command Executor",
                #            description=result,
                #            color=0x9CAFBE,
                #            inline=True)
                await message.channel.send(content=str(message.guild.roles))
    if command == "$guilds":
        await message.channel.send(client.guilds)
    if command == '$extid':
        try:
            target = await client.fetch_user(int(text[1]))
        except:
            await  message.channel.send("Could not find user")
            return
        embed=discord.Embed(title="External ID Search",
                            description=text[1],
                            colour=discord.Colour.from_rgb(255, 0, 242)
                            )\
            .add_field(name="User", value=target.name+"#"+target.discriminator, inline=False)\
            .add_field(name="Registered:", value=str(target.created_at)[:-7])\
            .set_thumbnail(url=target.avatar_url)\
            .set_footer(text=message.author.name+"#"+message.author.discriminator+" | "+datetime.now().strftime("%b %d, %Y %H:%M:%S"), icon_url=message.author.avatar_url)
        if target.bot:
            embed.add_field(name="Bot User", value=":white_check_mark: True")
        else:
            embed.add_field(name="Bot User", value=":x: False")
        await message.channel.send(embed=embed)
        return "exit"
    if command == "$ping":
        await aspen.ping(client, message)
    return



