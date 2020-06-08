
import discord

#Image dupe checking
import hashlib
import urllib.request

#Misc
import platform
import subprocess
import sys
import json
import random
import re
import time
import math
import io
import sqlite3

#Async stuff
import asyncio
import aiohttp
import aiofiles
import concurrent.futures

global startTime
startTime = time.time()

#Create data directory, it will fail if it already exists so pass if errors
try:
    os.system("mkdir data")

except:
    pass

#Check if token file exists
try:
    f = open("data/token.data")
    f.read()
    f.close()

except:
    sys.exit("No token")

#Get token from file
f = open("data/token.data")
token = f.read().splitlines()[0]
f.close()

#Set prefix global
global prefix
prefix = ","

#Define Discord client object
global client
client = discord.Client()

#Perform background tasks asynchronously
async def backgroundLoop():
    while True:
        #Asynchronously read status from data/status.data
        f = await aiofiles.open("data/status.data")
        presence = await f.read()
        await f.close()

        #Every time Discord pushes a new build, the bot's presence gets reset, this just sets it every 10 minutes to ensure it's mostly always there
        await client.change_presence(activity=discord.Game(name=presence))
        asyncio.sleep(600)

#Change the bot's status
async def cmd_setstatus(message):
    #Check if message author is me
    if message.author.id == 245994206965792780:
        #Set status
        msg = message.content.replace("{}setpresence ".format(prefix),"")
        await client.change_presence(activity=discord.Game(name=msg))

        #Send confirmation message
        em = discord.Embed(title="Status",description=msg,colour=random.randint(0,16777215))
        await message.channel.send(embed=em)

        #Asynchronously store status in data/status.data
        f = await aiofiles.open("data/status.data","w+")
        await f.write(msg)
        await f.close()

    #If message author is not me
    else:
        #Send access denied message
        em = discord.Embed(title="Access Denied",description="I'm sorry, you are not a bot admin.",colour=16711680)
        await message.channel.send(embed=em)
        return

#Toggle deletion of reposts
async def cmd_toggle_deletion(message):
    if not message.author.guild_permissions.administrator:
        em = discord.Embed(title="Access Denied",description="You must be a server administrator to run this command.",colour=16711680)
        await message.channel.send(embed=em)
        return

    try:
        f = await aiofiles.open(f"data/{message.guild.id}/delete.data")
        contents = await f.read()
        await f.close()

    except:
        contents = ""

    if "1" in contents:
        f = await aiofiles.open(f"data/{message.guild.id}/delete.data","w+")
        await f.write("")
        await f.close()

        em = discord.Embed(title="Toggle Deletion",description="Deletion is now disabled", colour=random.randint(0,16777215))
        await message.channel.send(embed=em)

    else:
        f = await aiofiles.open(f"data/{message.guild.id}/delete.data","w+")
        await f.write("1")
        await f.close()

        em = discord.Embed(title="Toggle Deletion",description="Deletion is now enabled", colour=random.randint(0,16777215))
        await message.channel.send(embed=em)

#Info command
async def cmd_info(message):
    em = discord.Embed(title="Info",colour=random.randint(0,16777215))
    em.add_field(name="Invite Link",value="https://discordapp.com/oauth2/authorize?client_id=705916758371991642&scope=bot&permissions=67136512",inline=False)
    em.add_field(name="Users",inline=False,value=len(list(client.get_all_members())))
    em.add_field(name="Servers",inline=False,value=len(client.guilds))
    em.add_field(name="My Server",inline=False,value="https://discord.gg/GYUS2Jg")

    #Calculate uptime
    uptime = time.time() - startTime
    uptime = math.floor(uptime)
    seconds = uptime % 60
    minutes = math.floor(((uptime - seconds) / 60) % 60)
    hours = math.floor(minutes / 60)
    days = math.floor(hours / 24)
    uptime = "Days: {} , Hours: {} , Minutes: {} , Seconds: {}".format(days, hours, minutes, seconds)

    em.add_field(name="Uptime",inline=False,value=uptime)
    em.add_field(name="My Library",inline=False,value="I use discord.py")
    await message.channel.send(embed=em)

#Get Invite
async def cmd_invite(message):
    await message.channel.send("https://discordapp.com/oauth2/authorize?client_id=705916758371991642&scope=bot&permissions=67136512")

#Help command
async def cmd_help(message):
    em = discord.Embed(title="Help",description="Whenever a user sends a file or a link to a file (excluding Discord links), the bot logs it and increases that user's meme count which is displayed in the leaderboard channel. If the meme is reposted, the bot sends a message pinging the original sender.",colour=random.randint(0,16777215))
    em.add_field(name=f"{prefix}score",value="See your score",inline=False)
    em.add_field(name=f"{prefix}set_leaderboard",value="Set the leaderboard channel, it is advised that this channel is read only so that the leaderboard message is always visible",inline=False)
    em.add_field(name=f"{prefix}toggle_deletion",value="Toggle whether the bot deletes reposts",inline=False)
    em.add_field(name=f"{prefix}invite",value="Get the bot's invite link",inline=False)
    em.add_field(name=f"{prefix}info",value="Get info on the bot",inline=False)

    await message.channel.send(embed=em)

#Test command
async def cmd_ping(message):
    await message.channel.send("pong")

#View your score
async def cmd_score(message):
    #Asynchronously load guilds leaderboard
    f = await aiofiles.open(f"data/{message.guild.id}/leaderboard.data")
    leaderboard = await json.load(f)
    await f.close()

    #Get user's score
    score = leaderboard[str(message.author.id)]

    #Load everyone's score into a list
    positions = []
    for i in leaderboard:
        positions.append([int(leaderboard[i]),i])

    #Sort leaderboard
    positions.sort()

    #Get author's position on the leaderboard
    position = str(positions.index([int(score),str(message.author.id)])+1)

    #Some stupid code to add the correct suffix to the position
    try:
        if position[-1] == "1" and position[-2] != "1":
            position += "st"

        elif position[-1] == "2" and position[-2] != "1":
            position += "nd"

        elif position[-1] == "3" and position[-2] != "1":
            position += "rd"

        else:
            position += "th"

    except:
        if position[-1] == "1":
            position += "st"

        elif position[-1] == "2":
            position += "nd"

        elif position[-1] == "3":
            position += "rd"

        else:
            position += "th"

    #Create message embed
    em = discord.Embed(title="Your Score",colour=random.randint(0,16777215))
    em.add_field(name="Position",value=position)
    em.add_field(name="Score",value=score)

    await message.channel.send(embed=em)

#Send leaderboard message
async def cmd_set_leaderboard(message):
    #Check if message author has admin perms or manage channels perm
    if not (message.author.guild_permissions.administrator or message.author.guild_permissions.manage_channels):
        em = discord.Embed(title="Permissions Error",description="You need the manage channels permission to run this command",colour=16711680)
        await message.channel.send(embed=em)
        return

    #Send leaderboard message
    newmessage = await message.channel.send("***Leaderboard***")
    channelID = newmessage.channel.id
    messageID = newmessage.id

    try:
        #Create guild's data folder
        subprocess.Popen(f"mkdir \"data/{message.guild.id}\"",shell=True)

    except:
        pass

    #Write channel and message ID to ids.data
    f = await aiofiles.open(f"data/{message.guild.id}/ids.data","w+")
    await f.write(f"{channelID}\n{messageID}")
    await f.close()


@client.event
async def on_guild_join(guild):
    #DM me when the bot joins a new server
    me = client.get_user(245994206965792780)
    if me.dm_channel == None:
        await me.create_dm()

    await me.dm_channel.send(f"Joined server: {guild.name} ({guild.id}) with {str(len(guild.members))} members")

@client.event
async def on_guild_remove(guild):
    #DM me when the bot leaves a server
    me = client.get_user(245994206965792780)
    if me.dm_channel == None:
        await me.create_dm()

    await me.dm_channel.send(f"Left server: {guild.name} ({guild.id})")

#When bot is connected, print a message
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

def getHash(myString):
    return hashlib.md5(myString).hexdigest()

def regexSearch(term,myString):
    return re.search(term, myString).group("url")

@client.event
async def on_message(message):
    global prefix

    #Ignore messages from the bot (prevents looping by malicious parties)
    if message.author == client.user:
        return

    meme = False
    if len(message.attachments) > 0: #If the message has attachments
        meme = True #Define message as meme
        memeUrl = message.attachments[0].url #Assume message has only one attachment and get it's CDN url

        #await message.attachments[0].save(f"data/{message.guild.id}/temp") #Save the attachment to the temp file
        fd = io.BytesIO()
        await message.attachments[0].save(fd)
        #Read raw bytes from the temp file (the attachment)
        #f = await aiofiles.open(f"data/{message.guild.id}/temp","rb")
        contents = fd.read()
        fd.close()

        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        hash = await loop.run_in_executor(executor,getHash,contents) #Hash the raw attachment bytes (weird but I mean it works, if someone really wanted to get around the detection, it would be really easy though)
        print(str(hash))

    elif "https://" in message.content: #If the message contains a link
        meme = True #Define message as meme
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        memeUrl = await loop.run_in_executor(executor,regexSearch,"(?P<url>https?://[^\s]+)",message.content)

        async with aiohttp.ClientSession() as session:
            async with session.get(memeUrl) as resp:
                #fd = await aiofiles.open(f"data/{message.guild.id}/temp", 'wb')
                fd = io.BytesIO()
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    fd.write(chunk)

        #urllib.request.urlretrieve(memeUrl,f"data/{message.guild.id}/temp") #Save the link contents to temp (does not work with Discord CDN links as they have web scraper protection - even with user agent changed)
        #f = await aiofiles.open(f"data/{message.guild.id}/temp","rb") #Read raw bytes from the temp file (the link contents)
        contents = fd.read()
        fd.close()
        hash = await loop.run_in_executor(executor,getHash,contents) #Hash the raw attachment bytes (weird but I mean it works, if someone really wanted to get around the detection, it would be really easy though)


    if meme: #If message is a meme
        print("{} ({}) > {} ({}): Meme Detected".format(message.guild.name,message.guild.id,message.author.name,message.author.id)) #Log that a meme has been detected
        try:
            f = await aiofiles.open(f"data/{message.guild.id}/memes.data")
            memes = await f.read()
            memes = memes.splitlines() #Get a list of past meme hashes
            await f.close()

        #If file doesn't exist
        except:
            #Create file
            f = await aiofiles.open(f"data/{message.guild.id}/memes.data","w+")
            await f.close()
            #Set memes to blank
            memes = []

        for x in memes: #Run through the meme hashes
            if hash in x: #If message's meme hash is in the file
                delete = False
                try:
                    f = await aiofiles.open(f"data/{message.guild.id}/delete.data")
                    contents = await f.read()
                    await f.close()

                    if "1" in contents:
                        delete = True

                except:
                    pass

                if delete == False:
                    em = discord.Embed(title="Repost Detected!",description="This meme has already been sent, thief.",colour=16711680) #Define an angry embed (in red of course)
                    em.add_field(name="URL",value=memeUrl) #Attach url for the meme (in case of spam)

                    for i in memes: #Run through all the meme hashes
                        if hash in i: #If hash is current meme
                            i = i.replace(f"{hash} - ","") #Get original author ID
                            em.add_field(name="Original Author",value=f"<@{i}>") #Add author mention to embed

                    await message.channel.send(embed=em) #Send embed
                    return #Return to prevent leaderboard changes

                else:
                    await message.delete(delay=1.0)

        try:
            #Write meme hash to memes.data
            f = await aiofiles.open(f"data/{message.guild.id}/memes.data","a")
            await f.write(f"\n{hash} - {message.author.id}")
            await f.close()

        except:
            #Write meme hash to memes.data
            f = await aiofiles.open(f"data/{message.guild.id}/memes.data","w+")
            await f.write(f"\n{hash} - {message.author.id}")
            await f.close()

        try:
            #Load leaderboard into a dictionary
            f = await aiofiles.open(f"data/{message.guild.id}/leaderboard.data")
            content = await f.read()
            leaderboard = json.loads(content)
            await f.close()

        except:
            f = await aiofiles.open(f"data/{message.guild.id}/leaderboard.data","w+")
            await f.write("{}")
            await f.close()
            leaderboard = {}

        #Try to add 1 to author's score
        try:
            leaderboard[str(message.author.id)] = str(int(leaderboard[str(message.author.id)]) + 1)

        #If failed, author is not in leaderboard, add a new entry
        except:
            leaderboard[str(message.author.id)] = "1"

        #Dump dictionary to leaderboard.data
        f = await aiofiles.open(f"data/{message.guild.id}/leaderboard.data","w")
        toWrite = json.dumps(leaderboard)
        print(toWrite)
        await f.write(toWrite)
        await f.close()

        #Load dictionary into a 2d list (for ordering - dictionaries in Python are not ordered)
        positions = []
        for i in leaderboard:
            positions.append([int(leaderboard[i]),i])

        #Sort leaderboard
        positions.sort()
        content = "***Leaderboard***"

        for i in range(5): #Run through top 5 scores
            if i == 0: #Since list is being accessed from the end, 1 (-1) is the first index, not 0
                continue
            try: #Try to add score to content
                content = content + "\n" + str(i) + " - " + f"<@{positions[-i][1]}>" + " - " + str(positions[-i][0]) + " memes"
            except: #If failed, there are less than 5 entries, break the loop
                break

        try:
            f = await aiofiles.open(f"data/{message.guild.id}/ids.data")
            toSplit = await f.read()
            channelID,messageID = toSplit.splitlines()
            await f.close()

            #Edit the leaderboard to the new scores
            channel = client.get_channel(int(channelID))
            msg = await channel.fetch_message(int(messageID))
            await msg.edit(content=content)

        except:
            pass

    if message.content.startswith(prefix): #If message is command
        try:
            print("{} ({}) > {} ({}): {}".format(message.guild.name,message.guild.id,message.author.name,message.author.id,message.content)) #Log command
        except: #If fails, command was sent in a DM
            print("{} ({}): {}".format(message.author.name,message.author.id,message.content)) #Log command

        msg = message.content.replace(prefix,"")
        try:
            msg,_ = msg.split(" ",1) #Remove any command parameters (message object is passed to command so they can be re-extracted later)
        except:
            pass
        withoutPrefix = msg.replace(prefix,"") #Remove prefix

        await globals()["cmd_{}".format(withoutPrefix)](message) #I really love this line xD, run the commands matching function and pass it the message object

client.run(token) #Run the bot
