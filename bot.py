import discord
from discord.ext.commands import Bot
from discord.ext import commands
import requests
import json
import base64
import lzma
import os.path
import sys

if len(sys.argv) > 0:
    if sys.argv[1] == "--offline":
        OPEN_DISCORD = False

class Circle:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Slider:
    def __init__(self, x, y, sliderdata):
        self.x = x
        self.y = y
        spl = sliderdata.split("|")
        self.type = spl[0]
        # We need this to later calculate if the player stayed on the slider
        self.sliderdata = spl[1]


class MapReplay:
    def __init__(self):
        self.mapid = ""
        self.map = []
        self.circleSize = 4
        self.overallDifficulty = 9.3

        self.hitwindow50 = 150 + 50 * (5 - self.overallDifficulty) / 5
        self.hitwindow100 = 100 + 40 * (5 - self.overallDifficulty) / 5
        self.hitwindow300 = 50 + 30 * (5 - self.overallDifficulty) / 5

        # Store data about the replay:
        # 0 if hit the circle with a 300
        # 1 for a 100
        # 2 for a 50
        # 3 for a miss
        self.replay = []

    def loadMap(self):
        # TODO: Download map automatically from osu website.
        #       For now assume the map is downloaded.
        # url = "https://osu.ppy.sh/b/get_beatmaps?k={}&b={}".format(keys[1], mapid)
        # 1531044

        isMapData = False
        for line in open("data/{}.osu".format(self.mapid)):
            if isMapData:
                objData = line.strip().split(",")
                x = int(objData[0])
                y = int(objData[1])
                time = int(objData[2])
                type = int(objData[3])
                if type == 1:
                    self.map.append((time, Circle(x, y)))
                elif type == 2:
                    self.map.append((time, Slider(x, y, objData[5])))


            # Only use relevant data for map parsing.
            if line.strip() == "[HitObjects]":
                isMapData = True
            elif isMapData and line.strip() == "":
                isMapData = False


    def loadReplay(self, playerid):

        # If the replay is already downloaded, dont download again to save
        #  peppy's server.
        filename = "data/{}_{}".format(self.mapid, playerid)
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                replaydata = file.read()
        else:
            url = "https://osu.ppy.sh/api/get_replay?k={}&m=0&b={}&u={}".format(keys[1], self.mapid, playerid)
            print("Requesting Replay Data...")

            r = requests.get(url)
            json_data = json.loads(r.text)

            data = base64.b64decode(json_data["content"])
            replaydata = lzma.decompress(data).decode("utf-8")
            with open(filename, 'w') as f:
                f.write(replaydata)

        totalTime = 0
        objIdx = 0
        onlclick = False
        onrclick = False
        lclick = False
        rclick = False
        for mvpoint in replaydata.split(","):
            data = mvpoint.split("|")

            # Last line is empty
            if len(data) < 4:
                break

            time = int(data[0])
            x = float(data[1])
            y = float(data[2])
            key = int(data[3])

            # Checks which keys were pressed at which timestamp.
            k5 = key & 5 == 5
            k10 = key & 10 == 10

            onlclick = k5 and not lclick
            onrclick = k10 and not rclick

            lclick = k5
            rclick = k10
            # >>>

            totalTime += time

            # If a key was pressed, check if there is a hitobject within timeframe.
            if objIdx >= len(self.map):
                continue

            hittime = abs(totalTime - self.map[objIdx][0])
            if (onrclick or onlclick) and hittime < self.hitwindow50:
                if type(self.map[objIdx][1]) is Circle:
                    # Actually clicking on the circle.
                    if (x - self.map[objIdx][1].x)**2 + (y - self.map[objIdx][1].y)**2\
                        < (54.4 - 4.48 * self.circleSize)**2:

                        if hittime < self.hitwindow300:
                            pass
                        elif hittime < self.hitwindow100:
                            print("A 100 at circle: {}".format(objIdx))
                        else:
                            print("A 50")

                    else:
                        print("Missed circle: {}.".format(objIdx))
                else:
                    if (x - self.map[objIdx][1].x)**2 + (y - self.map[objIdx][1].y)**2\
                        < (54.4 - 4.48 * self.circleSize)**2:

                        pass

                    else:
                        print("Missed slider: {}.".format(objIdx))

                objIdx += 1



        return

async def get_mapdata(message, mapid, player):
    url = "https://osu.ppy.sh/api/get_beatmaps?k={}&b={}".format(keys[1], mapid)

    r = requests.get(url)
    data = json.loads(r.text)

    info = "{} [{}] ".format(data[0]["title"], data[0]["version"])

    url = "https://osu.ppy.sh/api/get_scores?k={}&m=0&b={}&u={}&type=string".format(keys[1], mapid, player)

    r = requests.get(url)
    data = json.loads(r.text)

    print(data)
    if len(data) == 0:
        await client.send_message(message.channel, "Something is wrong with this score/player.")
        return

    info += ", played by {}, currently worth {} pp".format(player, data[0]["pp"])

    await client.send_message(message.channel, info)


async def set_score(message, mapid, player, score):
    url = "https://osu.ppy.sh/api/get_beatmaps?k={}&b={}".format(keys[1], mapid)

    r = requests.get(url)
    data = json.loads(r.text)

    if len(data) == 0:
        await client.send_message(message.channel, "Something is wrong with this score/player.")
        return

    info = "{} [{}] ".format(data[0]["title"], data[0]["version"])


    json_obj = {}
    json_obj['mapid'] = mapid
    json_obj['player'] = player
    json_obj['score'] = score
    json_obj['mapname'] = data[0]["title"]
    json_obj['diff'] = data[0]["version"]
    json_data = json.dumps(json_obj)

    filename = "data/{}_{}".format(mapid, player)
    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            storeddata = json.load(file)
        await client.send_message(message.channel, "Previous set pp for {} [{}] by {} was {}".format(storeddata['mapname'], storeddata['diff'], storeddata["player"], storeddata["score"]))
    with open(filename, 'w') as file:
        file.write(json_data)
        await client.send_message(message.channel, "Set desired pp for {} [{}] by {} at {}".format(data[0]['title'], data[0]['version'], player, score))


client = discord.Client()


@client.event
async def on_message(message):
    msg_array = message.content.split()
    if len(msg_array) == 0:
        return

    cmd = msg_array[0]
    args = msg_array[1:]

    if cmd == "!getscore":
        if len(args) != 2:
            await client.send_message(message.channel, "Syntax: !getscore <mapid> <player>")
        else:
            await get_mapdata(message, args[0], args[1])

    if cmd == "!setscore":
        if len(args) != 3:
            await client.send_message(message.channel, "Syntax: !setscore <mapid> <player> <score>")
        else:
            await set_score(message, args[0], args[1], args[2])


with open('key', 'r') as f:
    keys = f.readlines()
keys = [x.strip() for x in keys]

if OPEN_DISCORD:
    client.run(keys[0])
else:
    # str = input("Please input a map id.\n").strip()

    str = "1531044"

    mapReplay = MapReplay()
    mapReplay.mapid = str
    mapReplay.loadMap()

    # str = input("Please input a player name.\n").strip()
    str = "minatozaki"

    mapReplay.loadReplay(str)
    client.close()
