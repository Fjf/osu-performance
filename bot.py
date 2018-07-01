import discord
from discord.ext.commands import Bot
from discord.ext import commands
import requests
import json
import base64
import lzma
import os.path
import sys
import os


# async def get_mapdata(message, mapid, player):
#     url = "https://osu.ppy.sh/api/get_beatmaps?k={}&b={}".format(keys[1], mapid)
#
#     r = requests.get(url)
#     data = json.loads(r.text)
#
#     info = "{} [{}] ".format(data[0]["title"], data[0]["version"])
#
#     url = "https://osu.ppy.sh/api/get_scores?k={}&m=0&b={}&u={}&type=string".format(keys[1], mapid, player)
#
#     r = requests.get(url)
#     data = json.loads(r.text)
#
#     if len(data) == 0:
#         await client.send_message(message.channel, "Something is wrong with this score/player.")
#         return
#
#     info += ", played by {}, currently worth {} pp".format(player, data[0]["pp"])
#
#     await client.send_message(message.channel, info)
#
#
# async def set_score(message, mapid, player, score):
#     url = "https://osu.ppy.sh/api/get_beatmaps?k={}&b={}".format(keys[1], mapid)
#
#     r = requests.get(url)
#     data = json.loads(r.text)
#
#     if len(data) == 0:
#         await client.send_message(message.channel, "Something is wrong with this score/player.")
#         return
#
#     info = "{} [{}] ".format(data[0]["title"], data[0]["version"])
#
#     json_obj = {}
#     json_obj['mapid'] = mapid
#     json_obj['player'] = player
#     json_obj['score'] = score
#     json_obj['mapname'] = data[0]["title"]
#     json_obj['diff'] = data[0]["version"]
#     json_data = json.dumps(json_obj)
#
#     filename = "data/{}_{}".format(mapid, player)
#     if os.path.isfile(filename):
#         with open(filename, 'r') as file:
#             storeddata = json.load(file)
#         await client.send_message(message.channel, "Previous set pp for {} [{}] by {} was {}".format(
# storeddata['mapname'], storeddata['diff'], storeddata["player"], storeddata["score"]))
#     with open(filename, 'w') as file:
#         file.write(json_data)
#         await client.send_message(message.channel, "Set desired pp for {} [{}] by {} at {}".format(data[0]['title'],
# data[0]['version'], player, score))
#
#
# client = discord.Client()
# @client.event
# async def on_message(message):
#     msg_array = message.content.split()
#     if len(msg_array) == 0:
#         return
#
#     cmd = msg_array[0]
#     args = msg_array[1:]
#
#     if cmd == "!setscore":
#         if len(args) != 3:
#             await client.send_message(message.channel, "Syntax: !setscore <mapid> <player> <score>")
#         else:
#             await set_score(message, args[0], args[1], args[2])
#
from downloaders.mapdownloader import MapDownloader
from replayanalyzer.mapreplay import analyze

if __name__ == "__main__":
    # Parse command line arguments.
    OPEN_DISCORD = True
    if len(sys.argv) > 0:
        if sys.argv[1] == "--offline":
            OPEN_DISCORD = False

    # Create folder for data if it doesnt exist yet.
    if not os.path.isdir("data/"):
        os.mkdir("data")

    # Read keys from file
    with open('key', 'r') as f:
        keys = f.readlines()
    keys = [x.strip() for x in keys]

    # if OPEN_DISCORD:
    #     client.run(keys[0])
    # else:

    map_downloader = MapDownloader(keys[2], keys[3])

    map_id = "1531044"
    map_downloader.download(map_id)

    analyze(keys[1], "naam", map_id)