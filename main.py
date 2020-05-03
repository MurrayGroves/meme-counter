
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

#Check if memes file exists, if not, make it
try:
    f = open("data/memes.data")
    f.read()
    f.close()

except:
    f = open("data/memes.data", "w+")
    f.write("")
    f.close()

#Check if leaderboard file exists, if not, make it
try:
    f = open("data/leaderboard.data")
    f.read()
    f.close()

except:
    f = open("data/leaderboard.data","w+")
    f.write("{}")
    f.close()

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
#Try to get channel and message IDs from file
try:
    f = open("data/ids.data")
    channelID,messageID = f.read().splitlines()
    f.close()

except: #If fail, check if in development or being hosted (crude I know, I might switch to using environment variables)
    if platform.system() == "Windows":
        channelID = 705851333147754509
        messageID = 705854918463848509

    else:
        channelID = 705916979814596678
        messageID = 705917546834034698

#Test command
async def cmd_ping(message):
    await message.channel.send("pong")

#Send leaderboard message
async def cmd_set_leaderboard(message):
    channelID = message.channel.id
    messageID = message.id

    #Write channel and message ID to ids.data
    f = open("data/ids.data","w+")
    f.write(f"{channelID}\n{messageID}")
    f.close()

    await message.channel.send("***Leaderboard***")

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
    fileSaved = False
    if len(message.attachments) > 0: #If the message has attachments
        meme = True #Define message as meme
        memeUrl = message.attachments[0].url #Assume message has only one attachment and get it's CDN url
        fileSaved = True
        #memeUrl = re.search("(?P<url>https?://[^\s]+)", memeUrl).group("url")
        f = open("temp","wb") #Open temp in write bytes mode
        await message.attachments[0].save(f) #Save the attachment to the temp file
        f.close()

        #Read raw bytes from the temp file (the attachment)
        f = open("temp","rb")
        contents = f.read()
        f.close()

        hash = hashlib.md5(contents).hexdigest() #Hash the raw attachment bytes (weird but I mean it works, if someone really wanted to get around the detection, it would be really easy though)

    elif "https://" in message.content: #If the message contains a link
        meme = True #Define message as meme
        memeUrl = re.search("(?P<url>https?://[^\s]+)", message.content).group("url") #Extract the url from the message

        urllib.request.urlretrieve(memeUrl,"temp") #Save the link contents to temp (does not work with Discord CDN links as they have web scraper protection - even with user agent changed, I could just pretend that's to stop people from taking memes from other people though)
        f = open("temp","rb") #Read raw bytes from the temp file (the link contents)
        contents = f.read()
        f.close()
        hash = hashlib.md5(contents).hexdigest() #Hash the raw bytes (weird but it works)

    if meme: #If message is a meme
        print("meme") #Scientifically log that a meme was detected
        f = open("data/memes.data")
        memes = f.read().splitlines() #Get a list of past meme hashes
        for x in memes: #Run through the meme hashes
            if hash in x: #If message's meme hash is in the file
                em = discord.Embed(title="Don't steal fucker",description="This meme has already been sent idiot",colour=16711680) #Define an angry embed (in red of course)
                em.add_field(name="URL",value=memeUrl) #Attach url for the meme (in case of spam)

                for i in memes: #Run through all the meme hashes
                    if hash in i: #If hash is current meme
                        i = i.replace(f"{hash} - ","") #Get original author ID
                        em.add_field(name="Original Author",value=f"<@{i}>") #Add author mention to embed

                await message.channel.send(embed=em) #Send embed
                return #Return to prevent leaderboard changes

        #Write meme hash to memes.data
        f = open("data/memes.data","a")
        f.write(f"\n{hash} - {message.author.id}")
        f.close()

        #Load leaderboard into a dictionary
        f = open("data/leaderboard.data")
        leaderboard = json.load(f)
        f.close()

        #Try to add 1 to author's score
        try:
            leaderboard[str(message.author.id)] = str(int(leaderboard[str(message.author.id)]) + 1)

        #If failed, author is not in leaderboard, add a new entry
        except:
            leaderboard[str(message.author.id)] = "1"

        #Dump dictionary to leaderboard.data
        f = open("data/leaderboard.data","w")
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

        user = client.get_user(int(positions[-1][1]))
        await client.change_presence(activity=discord.Game(name=f"@{user.name} - {positions[-1][0]}"))

        for i in range(5): #Run through top 5 scores
            if i == 0: #Since list is being accessed from the end, 1 (-1) is the first index, not 0
                continue
            try: #Try to add score to content
                content = content + "\n" + str(i) + " - " + f"<@{positions[-i][1]}>" + " - " + str(positions[-i][0])
            except: #If failed, there are less than 5 entries, break the loop
                break

        #Edit the leaderboard to the new scores
        channel = client.get_channel(channelID)
        msg = await channel.fetch_message(messageID)
        await msg.edit(content=content)

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
