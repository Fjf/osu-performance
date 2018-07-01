import base64
import json
import lzma
import os

import requests

from downloaders.replay_downloader import download_replay


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
        if self.type == "L":
            self.end_x = spl[1].split(":")[0]
            self.end_y = spl[1].split(":")[1]
            pass
        elif self.type == "P":
            pass
        elif self.type == "B":
            pass
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

        is_map_data = False
        for line in open("data/{}.osu".format(self.map_id), encoding="utf-8"):
            if is_map_data:
                obj_data = line.strip().split(",")

                x = int(obj_data[0])
                y = int(obj_data[1])
                time = int(obj_data[2])
                type = int(obj_data[3])
                if type % 4 == 1:  # %4, to also catch the circles that start new combo
                    self.map.append((time, Circle(x, y)))
                elif type % 4 == 2:  # %4, to also catch the sliders that start new combo
                    self.map.append((time, Slider(x, y, obj_data[5])))

            # Only use relevant data for map parsing.
            if line.strip() == "[HitObjects]":
                is_map_data = True
            elif is_map_data and line.strip() == "":
                is_map_data = False

    def load_replay(self, player_id):
        replay_data = download_replay(self.api_key, player_id, self.map_id)

        total_time = 0
        obj_idx = 0
        l_click = False
        r_click = False
        for move_point in replay_data.split(","):
            data = move_point.split("|")

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

            on_l_click = k5 and not l_click
            on_r_click = k10 and not r_click

            l_click = k5
            r_click = k10

            total_time += time

            # If a key was pressed, check if there is a hitobject within timeframe.
            if obj_idx >= len(self.map):
                continue

            hit_time = abs(total_time - self.map[obj_idx][0])
            if (on_r_click or on_l_click) and hit_time < self.hitwindow50:
                if type(self.map[obj_idx][1]) is Circle:
                    # Actually clicking on the circle.
                    if (x - self.map[obj_idx][1].x)**2 + (y - self.map[obj_idx][1].y)**2 \
                            < (54.4 - 4.48 * self.circleSize)**2:

                        if hit_time < self.hitwindow300:
                            pass
                        elif hit_time < self.hitwindow100:
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


def analyze(api_key, name, map_id):
    map_replay = MapReplay(api_key)

    map_replay.map_id = map_id
    map_replay.load_map()
    map_replay.load_replay(name)