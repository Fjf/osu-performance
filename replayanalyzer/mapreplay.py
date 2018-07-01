import base64
import json
import lzma
import os

import requests


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
    def __init__(self, api_key):
        self.map_id = ""
        self.map = []
        self.circleSize = 4
        self.overallDifficulty = 9.3
        self.api_key = api_key

        self.hitwindow50 = 150 + 50 * (5 - self.overallDifficulty) / 5
        self.hitwindow100 = 100 + 40 * (5 - self.overallDifficulty) / 5
        self.hitwindow300 = 50 + 30 * (5 - self.overallDifficulty) / 5

        # Store data about the replay:
        # 0 if hit the circle with a 300
        # 1 for a 100
        # 2 for a 50
        # 3 for a miss
        self.replay = []

    def load_map(self):
        # TODO: Download map automatically from osu website.
        #       For now assume the map is downloaded.
        # url = "https://osu.ppy.sh/b/get_beatmaps?k={}&b={}".format(keys[1], map_id)
        # 1531044

        isMapData = False
        for line in open("data/{}.osu".format(self.map_id), encoding="utf-8"):
            if isMapData:
                objData = line.strip().split(",")

                x = int(objData[0])
                y = int(objData[1])
                time = int(objData[2])
                type = int(objData[3])
                if type % 4 == 1:  # %4, to also catch the circles that start new combo
                    self.map.append((time, Circle(x, y)))
                elif type % 4 == 2:  # %4, to also catch the sliders that start new combo
                    self.map.append((time, Slider(x, y, objData[5])))

            # Only use relevant data for map parsing.
            if line.strip() == "[HitObjects]":
                isMapData = True
            elif isMapData and line.strip() == "":
                isMapData = False

    def load_replay(self, player_id):
        # If the replay is already downloaded, dont download again to save
        #  peppy's server.
        filename = "data/{}_{}".format(self.map_id, player_id)
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                replaydata = file.read()
        else:
            url = "https://osu.ppy.sh/api/get_replay?k={}&m=0&b={}&u={}".format(self.api_key, self.map_id, player_id)
            print("Requesting Replay Data...")

            r = requests.get(url)
            json_data = json.loads(r.text)

            data = base64.b64decode(json_data["content"])
            replaydata = lzma.decompress(data).decode("utf-8")
            with open(filename, 'w') as f:
                f.write(replaydata)

        total_time = 0
        obj_idx = 0
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

            total_time += time

            # If a key was pressed, check if there is a hitobject within timeframe.
            if obj_idx >= len(self.map):
                continue

            hittime = abs(total_time - self.map[obj_idx][0])
            if (onrclick or onlclick) and hittime < self.hitwindow50:
                if type(self.map[obj_idx][1]) is Circle:
                    # Actually clicking on the circle.
                    if (x - self.map[obj_idx][1].x)**2 + (y - self.map[obj_idx][1].y)**2 \
                            < (54.4 - 4.48 * self.circleSize)**2:

                        if hittime < self.hitwindow300:
                            pass
                        elif hittime < self.hitwindow100:
                            print("A 100 at circle: {}".format(obj_idx))
                        else:
                            print("A 50")

                    else:
                        print("Missed circle: {}.".format(obj_idx))
                else:
                    if (x - self.map[obj_idx][1].x)**2 + (y - self.map[obj_idx][1].y)**2\
                            < (54.4 - 4.48 * self.circleSize)**2:

                        pass

                    else:
                        print("Missed slider: {}.".format(obj_idx))
                obj_idx += 1
        return


def analyze(api_key, map_id, name):
    map_replay = MapReplay(api_key)

    map_replay.map_id = map_id
    map_replay.load_map()
    map_replay.load_replay(name)