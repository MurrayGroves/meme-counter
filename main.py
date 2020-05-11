
import discord

#Image dupe checking
import hashlib
import urllib.request

#Misc
import platform
import os
import sys
import json
import random
import re
import time
import math

global startTime
startTime = time.time()

#Create data directory, it will fail if it already exists so pass if errors
try:
    os.system("mkdir data")

except:
    pass

#Check if token file exists, if not, exit. (Not a good idea to ask for input incase program is being run headless)
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


global channelID
global messageID

#Info command
async def cmd_info(message):
    em = discord.Embed(title="Info",colour=random.randint(0,16777215))
    em.add_field(name="Invite Link",value="https://discordapp.com/oauth2/authorize?client_id=705916758371991642&scope=bot&permissions=67136512",inline=False)
    em.add_field(name="Users",inline=False,value=len(list(client.get_all_members())))
    em.add_field(name="Servers",inline=False,value=len(client.guilds))
    em.add_field(name="My Server",inline=False,value="https://discord.gg/GYUS2Jg")
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
    em.add_field(name=f"{prefix}invite",value="Get the bot's invite link",inline=False)
    em.add_field(name=f"{prefix}info",value="Get info on the bot",inline=False)

    await message.channel.send(embed=em)

#Test command
async def cmd_ping(message):
    await message.channel.send("pong")

#View your score
async def cmd_score(message):
    f = open(f"data/{message.guild.id}/leaderboard.data")
    leaderboard = json.load(f)
    f.close()

    memes = leaderboard[str(message.author.id)]

    positions = []
    for i in leaderboard:
        positions.append([int(leaderboard[i]),i])

    #Sort leaderboard
    positions.sort()

    position = str(positions.index([int(memes),str(message.author.id)])+1)

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

    em = discord.Embed(title="Score",colour=random.randint(0,16777215))
    em.add_field(name="Position",value=position)
    em.add_field(name="Memes",value=memes)

    await message.channel.send(embed=em)

#Send leaderboard message
async def cmd_set_leaderboard(message):
    if not (message.author.guild_permissions.administrator or message.author.guild_permissions.manage_channels):
        em = discord.Embed(title="Permissions Error",description="You need the manage channels permission to run this command",colour=16711680)
        await message.channel.send(embed=em)
        return

    newmessage = await message.channel.send("***Leaderboard***")
    channelID = newmessage.channel.id
    messageID = newmessage.id
    os.system(f"mkdir \"data/{message.guild.id}\"")

    #Write channel and message ID to ids.data
    f = open(f"data/{message.guild.id}/ids.data","w+")
    f.write(f"{channelID}\n{messageID}")
    f.close()


#When bot is connected, delete token from memory (why not, might as well) and print connected message
@client.event
async def on_ready():
    global token
    del token
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global prefix

    #Ignore messages from the bot
    if message.author == client.user:
        return

    meme = False
    if len(message.attachments) > 0: #If the message has attachments
        meme = True #Define message as meme
        memeUrl = message.attachments[0].url #Assume message has only one attachment and get it's CDN url
        f = open(f"data/{message.guild.id}/temp","wb") #Open temp in write bytes mode
        await message.attachments[0].save(f) #Save the attachment to the temp file
        f.close()

        #Read raw bytes from the temp file (the attachment)
        f = open(f"data/{message.guild.id}/temp","rb")
        contents = f.read()
        f.close()

        hash = hashlib.md5(contents).hexdigest() #Hash the raw attachment bytes (weird but I mean it works, if someone really wanted to get around the detection, it would be really easy though)

    elif "https://" in message.content: #If the message contains a link
        meme = True #Define message as meme
        memeUrl = re.search("(?P<url>https?://[^\s]+)", message.content).group("url") #Extract the url from the message

        urllib.request.urlretrieve(memeUrl,f"data/{message.guild.id}/temp") #Save the link contents to temp (does not work with Discord CDN links as they have web scraper protection - even with user agent changed)
        f = open(f"data/{message.guild.id}/temp","rb") #Read raw bytes from the temp file (the link contents)
        contents = f.read()
        f.close()
        hash = hashlib.md5(contents).hexdigest() #Hash the raw bytes (weird but it works)

    if meme: #If message is a meme
        print("meme") #Scientifically log that a meme was detected
        try:
            f = open(f"data/{message.guild.id}/memes.data")
            memes = f.read().splitlines() #Get a list of past meme hashes
            f.close()
        except:
            f = open(f"data/{message.guild.id}/memes.data","w+")
            f.close()
            f = open(f"data/{message.guild.id}/memes.data")
            memes = f.read().splitlines() #Get a list of past meme hashes
            f.close()

        for x in memes: #Run through the meme hashes
            if hash in x: #If message's meme hash is in the file
                em = discord.Embed(title="Repost Detected!",description="This meme has already been sent, thief.",colour=16711680) #Define an angry embed (in red of course)
                em.add_field(name="URL",value=memeUrl) #Attach url for the meme (in case of spam)

                for i in memes: #Run through all the meme hashes
                    if hash in i: #If hash is current meme
                        i = i.replace(f"{hash} - ","") #Get original author ID
                        em.add_field(name="Original Author",value=f"<@{i}>") #Add author mention to embed

                await message.channel.send(embed=em) #Send embed
                return #Return to prevent leaderboard changes

        #Write meme hash to memes.data
        f = open(f"data/{message.guild.id}/memes.data","a")
        f.write(f"\n{hash} - {message.author.id}")
        f.close()

        try:
            #Load leaderboard into a dictionary
            f = open(f"data/{message.guild.id}/leaderboard.data")
            leaderboard = json.load(f)
            f.close()

        except:
            f = open(f"data/{message.guild.id}/leaderboard.data","w+")
            f.write("{}")
            f.close()
            leaderboard = {}

        #Try to add 1 to author's score
        try:
            leaderboard[str(message.author.id)] = str(int(leaderboard[str(message.author.id)]) + 1)

        #If failed, author is not in leaderboard, add a new entry
        except:
            leaderboard[str(message.author.id)] = "1"

        #Dump dictionary to leaderboard.data
        f = open(f"data/{message.guild.id}/leaderboard.data","w")
        json.dump(leaderboard,f)
        f.close()

        #Load dictionary into a 2d list (for ordering - dictionaries in Python are not ordered)
        positions = []
        for i in leaderboard:
            positions.append([int(leaderboard[i]),i])

        #Sort leaderboard
        positions.sort()
        print(positions) #Print leaderboard for debugging purposes
        content = "***Leaderboard***"

        for i in range(5): #Run through top 5 scores
            if i == 0: #Since list is being accessed from the end, 1 (-1) is the first index, not 0
                continue
            try: #Try to add score to content
                content = content + "\n" + str(i) + " - " + f"<@{positions[-i][1]}>" + " - " + str(positions[-i][0]) + " memes"
            except: #If failed, there are less than 5 entries, break the loop
                break

        try:
            f = open(f"data/{message.guild.id}/ids.data")
            channelID,messageID = f.read().splitlines()
            f.close()

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
