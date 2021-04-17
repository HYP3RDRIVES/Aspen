import discord
import aspen
from aspen import  moderation, logevents
from datetime import datetime
import resource
import requests
import asyncio
rexpingcount = 1
async def init(client, message):
    global rexpingcount
#    if message.guild.id == 735872336045277234 and message.author.id != 193112730943750144:
#        await message.delete()
    if message.author.id == 193112730943750144:
        if "This is a legal message to confirm to the public that may find my previous messages that may contain the words “simp”, or may indicate that I could be a simp, that I am not in fact a simp. Everything I say is for jokes and jokes only, therefore I am not a simp in any way, shape or form. Also to note, I am presently not dating anyone online. Anything I say that could possibly indicate that I am dating someone presently is to be automatically invalidated, and is used for jokes and jokes only." in message.content:
            await message.delete()
    if message.webhook_id and message.guild.id == 806151212814565386:
        if "zain" in message.content.lower() and message.guild.id == 806151212814565386:
            await message.delete()
        if "hyper" in message.content.lower() and message.guild.id == 806151212814565386:
            await message.delete()
        if "𝔃𝓪𝓲𝓷" in message.content.lower() and message.guild.id == 806151212814565386:
            await message.delete()
        if "𝕫𝕒𝕚𝕟" in message.content.lower() and message.guild.id == 806151212814565386:
            await message.delete()
        return
    if message.author.id == 705075850655039568:
        for x in message.mentions:
            if x.id == 750835145556230206:
                await message.delete()
                role = discord.utils.get(message.guild.roles, name="Muted")
                await message.author.add_roles(role)
                await message.channel.send("<@705075850655039568> You pinged Tristin, you may not speak for"+str(rexpingcount*30)+" Seconds")
                await asyncio.sleep(30*rexpingcount)
                rexpingcount = rexpingcount+1
                await message.author.remove_roles(role)

    if "https://cdn.discordapp.com/attachments/825096484180983868/825247949877018633/unknown.png" in message.content.lower():
        await message.delete()
    if "--debug" in message.content and message.author.id == 193112730943750144:
        await message.channel.send(str(message.content.split()))
        print(message.content)
    member = await message.guild.fetch_member(message.author.id)
    if not member.guild_permissions.manage_messages:
        for x in ["discord.gg/", "discord.com/invite", "discordapp.com/invite", "watchanimeattheoffice.com/invite", "discord.co/invite"]:
            if x in message.content.lower():
                await message.delete()
                key = "Discord Invite Link"
                await logevents.filterLog(client, message, key)
                return
    if message.guild.id == 615608144726589457:
        role = discord.utils.get(message.guild.roles, id=int(826590327270801418))
        if role in message.author.roles:
            if "http" in message.content.lower():
                await message.delete()
    if message.guild.id == 735872336045277234:
        if "janis" in message.content.lower():
            if message.author.id == 599040744334032912 or message.author.id == 566118564717658114:
                await message.delete()
    words = ['jooo', 'joo', 'jo', 'bidin', 'yeal', 'docter','tourkey','suri', 'kalakeen']
    for wordie in words:
        if wordie in message.content.lower().split():
            await message.delete()
            return "exit"
    if message.content.lower().startswith("jooo"):
        await message.delete()
        return
    if message.author.id == 566118564717658114:
        rileybannedwords = ["rat","roro","reeree","riri","rara","riirii"]
        for x in rileybannedwords:
            if x in message.content.lower():
                await message.delete()
        return
    if message.content.startswith('STOP POSTING ABOUT AMONG US'):
        await message.delete()
    if message.content == "https://media.tenor.co/videos/acaca7edff9422b16208ce75dfe952e0/mp4" or message.content == "https://tenor.com/view/we-do-a-little-trolling-a-little-trolling-its-called-we-do-a-its-called-we-do-a-little-trolling-gif-20272799":
        await message.delete()
    if message.content.startswith('$ofd'):
        await message.delete()
        if message.author.id == 193112730943750144 or message.author.id == 219838416878174209:
            text = message.content.split()
            channel = client.get_channel(736432247842013234)
            msg = await channel.fetch_message(text[1])
            await msg.delete()
        else:
            return
            # embed = discord.Embed(
            #    title="Invalid Permissions!",
            #    description="Only **Moderators** may use the Delete command!",
            #    colour=discord.Colour.red()
            # )
            # await message.channel.send(embed=embed,delete_after=4)
            ##print(text[1])
    if message.author.bot:
        return
    for x in message.mentions:
        if (x == client.user):
            embed = discord.Embed(
                title="Aspen#8530",
                description="""A bot developed and maintained by <@193112730943750144>

Currently running **Aspen v1.1.1**

                    """
            )
            embed.set_footer(text="Message will delete after 30 seconds")
            embed.add_field(name="Shard ID",value=str(message.guild.shard_id))
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/avatars/371491028873773079/86216d3ef0a07016e5f287d6de7953ad.png")
            #print("Internal Chat Event at " + str(datetime.now()) + " in " + str(message.channel.id))
            await message.channel.send(embed=embed, delete_after=30)

    return


async def ext(client, message):
    text = message.content.split()
    if message.content.startswith('$ping'):
        await aspen.ping(client, message)
    if message.content.startswith("$av"):
        if message.content.split()[1] == "help":
            await message.channel.send(
                embed=discord.Embed(title="Avatar", description="Displays the Avatar of a selected user",
                                    colour=discord.Colour.from_rgb(255, 0, 242))
                .add_field(name="Permissions", value="Everyone")
                .add_field(name="Usage", value="$av <User>"))
            return
        target = await aspen.userArgParse(message, 1)
        if target is None:
            return
        avatar_loc = target.avatar_url
        embed = discord.Embed(title="Avatar for " + target.name + "#" + target.discriminator,
                              colour=discord.Colour.from_rgb(255, 0, 242))
        embed.set_image(url=avatar_loc)
        embed.set_author(name=message.author.name + "#" + message.author.discriminator,
                         icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    if message.content.lower().split()[0] == "$s":
        if message.author.id == 193112730943750144:
            text = message.content.split()
            if len(text) != 2:
                await message.channel.send("Invalid syntax")
                return
            r = requests.post("https://s.hypr.ax/shorten/"+text[1], headers={"Authorization":"DeyhX6AFpkV7uL93L4u6dCyaSbiyfFB4iQmLvhkx"})
            if r.status_code==200:
                await message.channel.send(r.text)
            else:
                await message.channel.send("Invalid URL")
                return
    if message.content.startswith('$invite'):
        if message.author.guild_permissions.administrator == True:
            link = await message.channel.create_invite(max_age=300)
            await message.channel.send("Here is an instant invite to your server: " + str(link))
    if message.content.startswith('$cdel'):
        text = message.content.split()
        await message.delete()
        if message.author.id != 193112730943750144:
            return
        channel = client.get_channel(text[1])
        msg = channel.fetch_message(text[2])
        await msg.delete()
    if message.content.startswith('$info'):
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
    if message.content.split()[0] == '$ban':
        if message.author.guild_permissions.ban_members:
            if len(text) == 1 or (len(text) == 2 and text[1] == "help"):
                await message.channel.send(embed=discord.Embed(title="Ban", description="Bans a member from the Server",
                                                               colour=discord.Colour.from_rgb(255, 0, 242))
                                           .add_field(name="Permissions", value="Ban Members")
                                           .add_field(name="Usage", value="$ban <User>"))
                return
            user = await aspen.userArgParse(message, 1)
            if user is None:
                return
            if user.id == 193112730943750144:
                await message.channel.send("You may not ban the **Bot Owner**")
                return
            await message.guild.ban(user=user,delete_message_days=0)
            await message.channel.send(embed=discord.Embed(title="User Banned!",description="Banned "+user.name+"#"+user.discriminator,colour=discord.Colour.red()))
    if message.content.split()[0] == '$cban':
        if message.author.id == 193112730943750144:
            if len(text) == 1:
                await message.channel.send(embed=discord.Embed(title="Contextual Ban", description="Bans a member from a specified guild",
                                                               colour=discord.Colour.from_rgb(255, 0, 242))
                                           .add_field(name="Permissions", value="Bot Owner")
                                           .add_field(name="Usage", value="$cban <Guild ID> <User ID>"))
                return
            user = aspen.userArgParse(message, 2)
            if user is None:
                return
            if user.id == 193112730943750144:
                await message.channel.send("You may not ban the **Bot Owner**")
                return
            guild = client.get_guild(int(text[1]))
            await guild.ban(user=user,delete_message_days=0)
            await message.channel.send(embed=discord.Embed(title="User Banned!",description="Banned "+user.name+"#"+user.discriminator,colour=discord.Colour.red()))

    if message.content.split()[0] == '$unban':
        if message.author.guild_permissions.ban_members:
            if len(text) == 1:
                await message.channel.send(
                    embed=discord.Embed(title="Contextual Ban", description="Bans a member from a specified guild",
                                        colour=discord.Colour.from_rgb(255, 0, 242))
                    .add_field(name="Permissions", value="Bot Owner")
                    .add_field(name="Usage", value="$cban <Guild ID> <User ID>"))
                return
            user = aspen.userArgParse(message, 1)
            if user is None:
                return
            await message.guild.unban(user)
            #
            #    await message.channel.send("User either not banned or not found")

    if message.content.startswith('$test'):
        #await message.channel.send("done")
        return
    if message.content.startswith('$echo'):
        if message.author.id == 193112730943750144:
            await message.channel.send(message.content)
    if message.author.id == 750835145556230206:
        for x in [":smiling_face_with_3_hearts:", "babe", "🥰"]:
            if x in message.content.lower():
                await message.delete()
    if message.content.startswith('$cat'):
        msg = await message.channel.send("Searching for a cat...")
        r = requests.get("http://aws.random.cat/meow")
        file = r.json()['file']
        embed = discord.Embed(title="Found a Cat! 😺", colour=discord.Colour.from_rgb(255,0,242))\
            .set_image(url=file)
        await msg.edit(embed=embed, content="\u2000")
    if message.content.startswith('$dog'):
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
    if message.content.startswith('$btest'):
        if message.author.id == 193112730943750144 or message.author.id == 750835145556230206 or message.author.id == 219838416878174209:
            print("ok")
        else:
            return
        text = message.content.split()
        await message.delete()
        if len(text) < 3:
            await message.channel.send("Incorrect!", delete_after=1)
        guild = client.get_guild(735872336045277234)
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
        if user.id == 193112730943750144:
            username = "TheНyperdrive"
        content = message.content.replace(text[0] + " " + text[1], "", 1)

        r = requests.post(
            "https://discord.com/api/webhooks/825258566310297620/GCEhYEtWMW_WH2HMZv4VSaALspiSa3Sc8M3hjnhGlqh-l7TBa1BbbFPL45HG2Xb1DHIG",
            headers={'User-Agent': 'Mozilla/5.0'},
            data={'content': content, 'username': username, 'avatar_url': pfp}
            )
        # #print(r.text)
    if message.content.startswith('$stest'):
        if message.author.id == 193112730943750144 or message.author.id == 750835145556230206 or message.author.id == 219838416878174209:
            print("ok")
        else:
            return
        text = message.content.split()
        await message.delete()
        if len(text) < 3:
            await message.channel.send("Incorrect!", delete_after=1)
        guild = client.get_guild(806151212814565386)
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
        if user.id == 193112730943750144:
            username = "TheНyperdrive"
        content = message.content.replace(text[0] + " " + text[1], "", 1)

        r = requests.post(
            "https://discord.com/api/webhooks/825097257107718204/F2Y-WLDChanW3YvA1GVVrp4zv8A_dBnQwM6yt8OxWyzE2GheIy0aWIkIMQQZoD2xyyc2",
            headers={'User-Agent': 'Mozilla/5.0'},
            data={'content': content, 'username': username, 'avatar_url': pfp}
            )
        # #print(r.text)
    if message.content.startswith('$msend'):
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
    if message.content.startswith('$ctest'):
        if message.author.id == 193112730943750144:
            print("ok")
        else:
            return
        text = message.content.split()
        await message.delete()
        if len(text) < 3:
            await message.channel.send("Incorrect!", delete_after=1)
            return
        guild = client.get_guild(603203154091311104)
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

        requests.post(
            "https://discord.com/api/webhooks/748793443177857035/8lSRw-21zGJfCO21D8BKZJjiC-R16pUBUIsYu9M6KZy0vEFlwnkLuTiFE3yMEljEUwxu",
            headers={'User-Agent': 'Mozilla/5.0'},
            data={'content': content, 'username': username, 'avatar_url': pfp}
        )
            # #print(r.text)
        if message.content.startswith('$msend'):
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
        # #print(r.text)
    if message.content.startswith('$roleiter'):
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
    if message.content.startswith('$extid'):
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
    return



