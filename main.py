import discord
import json
import random
import threading
import asyncio
import re
import hashlib
import urllib.request

#Get token from file
f = open("data/token.data")
token = f.read().splitlines()[0]
f.close()

global prefix
prefix = ","

global client
client = discord.Client()

async def cmd_ping(message):
    await message.channel.send("pong")

async def cmd_set_leaderboard(message):
    em = discord.Embed(title="Leaderboard",colour=65280)
    await message.channel.send(embed=em)

@client.event
async def on_ready():
    global token
    del token
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global prefix

    if message.author == client.user:
        return

    meme = False
    fileSaved = False
    if len(message.attachments) > 0:
        meme = True
        memeUrl = message.attachments[0].url
        fileSaved = True
        memeUrl = re.search("(?P<url>https?://[^\s]+)", memeUrl).group("url")
        f = open("temp","wb")
        await message.attachments[0].save(f)
        f.close()
        f = open("temp","rb")
        contents = f.read()
        f.close()
        hash = hashlib.md5(contents).hexdigest()

    elif "https://" in message.content:
        meme = True
        memeUrl = re.search("(?P<url>https?://[^\s]+)", message.content).group("url")

        urllib.request.urlretrieve(memeUrl,"temp")
        f = open("temp")
        contents = f.read()
        f.close()
        hash = hashlib.md5(contents).hexdigest()

    if meme:

        print("meme")
        f = open("data/leaderboard.data")
        leaderboard = json.load(f)
        f.close()

        try:
            leaderboard[str(message.author.id)] = str(int(leaderboard[str(message.author.id)]) + 1)

        except:
            leaderboard[str(message.author.id)] = "1"

        f = open("data/leaderboard.data","w")
        json.dump(leaderboard,f)
        f.close()

        f = open("data/memes.data")
        memes = f.read().splitlines()
        for x in memes:
            if hash in x:
                em = discord.Embed(title="Nice One Retard",description="This meme has already been sent idiot")
                em.add_field(name="URL",value=memeUrl)

                f = open("data/memes.data")
                memes = f.read().splitlines()
                f.close()

                for i in memes:
                    if hash in i:
                        i = i.replace(f"{hash} - ","")
                        em.add_field(name="Original Author",value=f"<@{i}>")

                await message.channel.send(embed=em)
                return

        f = open("data/memes.data","a")
        f.write(f"\n{hash} - {message.author.id}")
        f.close()

        positions = []
        f = open("data/leaderboard.data")
        leaderboard = json.load(f)
        f.close()

        for i in leaderboard:
            positions.append([int(leaderboard[i]),i])

        positions.sort()
        print(positions)
        content = "***Leaderboard***"
        for i in range(5):
            if i == 0:
                continue
            try:
                content = content + "\n" + str(i) + " - " + f"<@{positions[-i][1]}>" + " - " + str(positions[-i][0])
            except:
                break

        channel = client.get_channel(705851333147754509)
        msg = await channel.fetch_message(705854918463848509)
        await msg.edit(content=content)

    if message.content.startswith(prefix):
        try:
            print("{} ({}) > {} ({}): {}".format(message.guild.name,message.guild.id,message.author.name,message.author.id,message.content))
        except:
            print("{} ({}): {}".format(message.author.name,message.author.id,message.content))
        msg = message.content.replace(prefix,"")
        try:
            msg,_ = msg.split(" ",1)
        except:
            msg = msg
        withoutPrefix = msg.replace(prefix,"")
        await globals()["cmd_{}".format(withoutPrefix)](message)

client.run(token)
