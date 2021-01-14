import discord

# Image handling
from PIL import Image
import numpy as np

# Misc
import subprocess
import sys
import json
import random
import re
import time
import math
import os

# Async stuff
import asyncio
import aiohttp
import aiofiles
import concurrent.futures

global startTime
startTime = time.time()

# Create data directory, it will error if it already exists so pass if errors
try:
    os.system("mkdir data")

except:
    pass

# Check if token file exists
try:
    f = open("data/token.data")
    f.read()
    f.close()

except:
    sys.exit("No token")

# Get token from file
f = open("data/token.data")
token = f.read().splitlines()[0]
f.close()

# Set prefix
prefix = ","

# Define Discord client object
global client
client = discord.Client()

import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})

# Perform background tasks asynchronously
async def backgroundLoop():
    while True:
        # Asynchronously read status from data/status.data
        f = await aiofiles.open("data/status.data")
        presence = await f.read()
        await f.close()

        # Every time Discord pushes a new build, the bot's presence gets reset, this just sets it every 10 minutes to ensure it's mostly always there
        await client.change_presence(activity=discord.Game(name=presence))
        asyncio.sleep(600)


# Change the bot's status
async def cmd_setstatus(message):
    # Check if message author is me
    if message.author.id == 245994206965792780:
        # Set status
        msg = message.content.replace("{}setstatus ".format(prefix), "")
        await client.change_presence(activity=discord.Game(name=msg))

        # Send confirmation message
        em = discord.Embed(
            title="Status", description=msg, colour=random.randint(0, 16777215)
        )
        await message.channel.send(embed=em)

        # Asynchronously store status in data/status.data
        f = await aiofiles.open("data/status.data", "w+")
        await f.write(msg)
        await f.close()

    # If message author is not me
    else:
        # Send access denied message
        em = discord.Embed(
            title="Access Denied",
            description="I'm sorry, you are not a bot admin.",
            colour=16711680,
        )
        await message.channel.send(embed=em)
        return


# Toggle deletion of reposts
async def cmd_toggle_deletion(message):
    if not message.author.guild_permissions.administrator:
        em = discord.Embed(
            title="Access Denied",
            description="You must be a server administrator to run this command.",
            colour=16711680,
        )
        await message.channel.send(embed=em)
        return

    try:
        f = await aiofiles.open(f"data/{message.guild.id}/delete.data")
        contents = await f.read()
        await f.close()

    except:
        contents = ""

    if "1" in contents:
        f = await aiofiles.open(f"data/{message.guild.id}/delete.data", "w+")
        await f.write("")
        await f.close()

        em = discord.Embed(
            title="Toggle Deletion",
            description="Deletion is now disabled",
            colour=random.randint(0, 16777215),
        )
        await message.channel.send(embed=em)

    else:
        f = await aiofiles.open(f"data/{message.guild.id}/delete.data", "w+")
        await f.write("1")
        await f.close()

        em = discord.Embed(
            title="Toggle Deletion",
            description="Deletion is now enabled",
            colour=random.randint(0, 16777215),
        )
        await message.channel.send(embed=em)


# Set percentage threshold for message to be marked as repost
async def cmd_set_threshold(message):
    # Check if message author has manage channels permission
    if not (
        message.author.guild_permissions.administrator
        or message.author.guild_permissions.manage_channels
    ):
        em = discord.Embed(
            title="Permissions Error",
            description="You need the manage channels permission to run this command",
            colour=16711680,
        )
        await message.channel.send(embed=em)
        return

    threshold = message.content.replace(f"{prefix}set_threshold ", "", 1)

    valid = True
    try:
        if int(threshold) > 100 or int(threshold) < 0:
            valid = False

    except:
        valid = False

    if not valid:
        em = discord.Embed(
            title="Error",
            description="The threshold must be a number between 0 and 100, "
            "representing the required percentage similarity "
            "between two images for them to be considered the "
            "same. Default is 25",
            colour=16711680,
        )

        await message.channel.send(embed=em)
        return

    f = await aiofiles.open(f"data/{message.guild.id}/threshold.data", "w+")
    await f.write(threshold)
    await f.close()

    em = discord.Embed(
        title="Set Threshold",
        description=f"Threshold set to {threshold}",
        colour=random.randint(0, 16777215),
    )

    await message.channel.send(embed=em)


# Info command
async def cmd_info(message):
    em = discord.Embed(title="Info", colour=random.randint(0, 16777215))
    em.add_field(
        name="Invite Link",
        value="https://discordapp.com/oauth2/authorize?client_id=705916758371991642&scope=bot&permissions=67136512",
        inline=False,
    )
    em.add_field(name="Users", inline=False, value=len(list(client.get_all_members())))
    em.add_field(name="Servers", inline=False, value=len(client.guilds))
    em.add_field(name="My Server", inline=False, value="https://discord.gg/GYUS2Jg")

    # Calculate uptime
    uptime = time.time() - startTime
    uptime = math.floor(uptime)
    seconds = uptime % 60
    minutes = math.floor(((uptime - seconds) / 60) % 60)
    hours = math.floor(minutes / 60)
    days = math.floor(hours / 24)
    uptime = "Days: {} , Hours: {} , Minutes: {} , Seconds: {}".format(
        days, hours, minutes, seconds
    )

    em.add_field(name="Uptime", inline=False, value=uptime)
    em.add_field(name="My Library", inline=False, value="I use discord.py")
    await message.channel.send(embed=em)


# Get Invite
async def cmd_invite(message):
    await message.channel.send(
        "https://discordapp.com/oauth2/authorize?client_id=705916758371991642&scope=bot&permissions=26640"
    )


# Help command
async def cmd_help(message):
    em = discord.Embed(
        title="Help",
        description="Whenever a user sends a file or a link to a file (excluding Discord links), the bot logs it and increases that user's meme count which is displayed in the leaderboard channel. If the meme is reposted, the bot sends a message pinging the original sender.",
        colour=random.randint(0, 16777215),
    )
    em.add_field(name=f"{prefix}score", value="See your score", inline=False)
    em.add_field(
        name=f"{prefix}set_threshold",
        value="Change what percentage "
        "similarity counts as a "
        "repost, should be a "
        "number between 0 and 100",
        inline=False,
    )
    em.add_field(
        name=f"{prefix}set_leaderboard",
        value="Override the leaderboard channel to current channel",
        inline=False,
    )
    em.add_field(
        name=f"{prefix}invite", value="Get the bot's invite link", inline=False
    )
    em.add_field(name=f"{prefix}info", value="Get info on the bot", inline=False)

    await message.channel.send(embed=em)


# Test command
async def cmd_ping(message):
    await message.channel.send("pong")


# View your score
async def cmd_score(message):
    # Asynchronously load guilds leaderboard
    f = await aiofiles.open(f"data/{message.guild.id}/leaderboard.data")
    content = await f.read()
    await f.close()
    leaderboard = json.loads(content)

    # Get user's score
    score = leaderboard[str(message.author.id)]

    # Load everyone's score into a list
    positions = []
    for i in leaderboard:
        positions.append([int(leaderboard[i]), i])

    # Sort leaderboard
    positions.sort()

    # Get author's position on the leaderboard
    position = str(positions.index([int(score), str(message.author.id)]) + 1)

    # Some stupid code to add the correct suffix to the position
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

    # Create message embed
    em = discord.Embed(title="Your Score", colour=random.randint(0, 16777215))
    em.add_field(name="Position", value=position)
    em.add_field(name="Score", value=score)

    await message.channel.send(embed=em)


# Send leaderboard message
async def cmd_set_leaderboard(message):
    # Check if message author has admin perms or manage channels perm
    if not (
        message.author.guild_permissions.administrator
        or message.author.guild_permissions.manage_channels
    ):
        em = discord.Embed(
            title="Permissions Error",
            description="You need the manage channels permission to run this command",
            colour=16711680,
        )
        await message.channel.send(embed=em)
        return

    # Send leaderboard message
    newmessage = await message.channel.send("***Leaderboard***")
    channelID = newmessage.channel.id
    messageID = newmessage.id

    try:
        # Create guild's data folder
        subprocess.Popen(f'mkdir "data/{message.guild.id}"', shell=True)

    except:
        pass

    # Write channel and message ID to ids.data
    f = await aiofiles.open(f"data/{message.guild.id}/ids.data", "w+")
    await f.write(f"{channelID}\n{messageID}")
    await f.close()


@client.event
async def on_guild_join(guild):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False),
        guild.me: discord.PermissionOverwrite(send_messages=True),
    }
    leaderboardChannel = await guild.create_text_channel(
        "meme-leaderboard", overwrites=overwrites
    )

    leaderboardMessage = await leaderboardChannel.send("***Leaderboard***")
    try:
        # Create guild's data folder
        subprocess.Popen(f'mkdir "data/{guild.id}"', shell=True)

    except:
        pass

    await asyncio.sleep(0.5)
    f = await aiofiles.open(f"data/{guild.id}/ids.data", "w+")
    await f.write(f"{leaderboardChannel.id}\n{leaderboardMessage.id}")
    await f.close()

    # DM me when the bot joins a new server
    me = client.get_user(245994206965792780)
    if me.dm_channel == None:
        await me.create_dm()

    await me.dm_channel.send(
        f"Joined server: {guild.name} ({guild.id}) with {str(len(guild.members))} members"
    )


@client.event
async def on_guild_remove(guild):
    # DM me when the bot leaves a server
    me = client.get_user(245994206965792780)
    if me.dm_channel == None:
        await me.create_dm()

    await me.dm_channel.send(f"Left server: {guild.name} ({guild.id})")


# When bot is connected, print a message
@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


# Function to use regex on given string
def regexSearch(term, myString):
    return re.search(term, myString).group("url")

# Run upon receiving message
@client.event
async def on_message(message):
    if message.guild.id == 110373943822540800:
        return

    global prefix

    # Ignore messages from the bot (prevents looping by malicious parties)
    if message.author == client.user:
        return

    meme = False
    if len(message.attachments) > 0:  # If the message has attachments
        meme = True  # Define message as meme

        curFilePath = f"{message.id}{os.path.splitext(message.attachments[0].filename)[1]}"
        f = open(f"images/{curFilePath}", "wb+")
        await message.attachments[0].save(f)
        f.close()

        im = Image.open(f"images/{curFilePath}")
        im_resize = im.resize((500, 500))
        im_resize.save(f"images/{curFilePath}")

    elif "https://" in message.content:  # If the message contains a link
        meme = True  # Define message as meme
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        memeUrl = await loop.run_in_executor(
            executor, regexSearch, "(?P<url>https?://[^\s]+)", message.content
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(memeUrl) as resp:

                contents = b""
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    contents += chunk


    if meme:  # If message is a meme

        from imagededup.methods import CNN
        phasher = CNN()
        encodings = phasher.encode_images(image_dir=f'images')
        duplicates = phasher.find_duplicates(encoding_map=encodings, scores=True, min_similarity_threshold=0.8)

        if len(duplicates[curFilePath]) > 0:
            stolen = True
            os.remove(f"images/{curFilePath}")
            origMessage = await message.channel.fetch_message(os.path.splitext(duplicates[curFilePath][0][0])[0])
            confidence = f"{int(round(duplicates[curFilePath][0][1],2)*100)}%"
            em = discord.Embed(title="Repost Detected", description=f"Matches [this post]({origMessage.jump_url}) from <@{origMessage.author.id}> with {confidence} confidence.", colour=16711680)
            await message.channel.send(embed=em)

        else:
            stolen = False

            try:
                # Load leaderboard into a dictionary
                f = await aiofiles.open(f"data/{message.guild.id}/leaderboard.data")
                content = await f.read()
                leaderboard = json.loads(content)
                await f.close()

            except:
                f = await aiofiles.open(
                    f"data/{message.guild.id}/leaderboard.data", "w+"
                )
                await f.write("{}")
                await f.close()
                leaderboard = {}

            # Try to add 1 to author's score
            try:
                leaderboard[str(message.author.id)] = str(
                    int(leaderboard[str(message.author.id)]) + 1
                )

            # If failed, author is not in leaderboard, add a new entry
            except:
                leaderboard[str(message.author.id)] = "1"

            # Dump dictionary to leaderboard.data
            f = await aiofiles.open(f"data/{message.guild.id}/leaderboard.data", "w")
            toWrite = json.dumps(leaderboard)
            await f.write(toWrite)
            await f.close()

            # Load dictionary into a 2d list (for ordering - dictionaries in Python are not ordered)
            positions = []
            for i in leaderboard:
                positions.append([int(leaderboard[i]), i])

            # Sort leaderboard
            positions.sort()
            content = "***Leaderboard***"

            for i in range(5):  # Run through top 5 scores
                if (
                    i == 0
                ):  # Since list is being accessed from the end, 1 (-1) is the first index, not 0
                    continue
                try:  # Try to add score to content
                    content = (
                        content
                        + "\n"
                        + str(i)
                        + " - "
                        + f"<@{positions[-i][1]}>"
                        + " - "
                        + str(positions[-i][0])
                        + " memes"
                    )
                except:  # If failed, there are less than 5 entries, break the loop
                    break

            try:
                f = await aiofiles.open(f"data/{message.guild.id}/ids.data")
                toSplit = await f.read()
                channelID, messageID = toSplit.splitlines()
                await f.close()

                # Edit the leaderboard to the new scores
                channel = client.get_channel(int(channelID))
                msg = await channel.fetch_message(int(messageID))
                await msg.edit(content=content)

            except:
                pass

    if message.content.startswith(prefix):  # If message is command
        try:
            print(
                "{} ({}) > {} ({}): {}".format(
                    message.guild.name,
                    message.guild.id,
                    message.author.name,
                    message.author.id,
                    message.content,
                )
            )  # Log command
        except:  # If fails, command was sent in a DM
            print(
                "{} ({}): {}".format(
                    message.author.name, message.author.id, message.content
                )
            )  # Log command

        msg = message.content.replace(prefix, "")
        try:
            msg, _ = msg.split(
                " ", 1
            )  # Remove any command parameters (message object is passed to command so they can be re-extracted later)
        except:
            pass
        withoutPrefix = msg.replace(prefix, "")  # Remove prefix

        await globals()["cmd_{}".format(withoutPrefix)](
            message
        )  # I really love this line xD, run the commands matching function and pass it the message object


client.run(token)  # Run the bot
