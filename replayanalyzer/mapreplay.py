from downloaders.replay_downloader import download_replay
from replayanalyzer.map_parser import Map
from replayanalyzer.objects import Circle


class MapReplay:
    def __init__(self, api_key):
        self.map_id = ""
        self.map = None
        self.api_key = api_key

        self.hit_window50 = -1
        self.hit_window100 = -1
        self.hit_window300 = -1

        # Store data about the replay:
        # 0 if hit the circle with a 300
        # 1 for a 100
        # 2 for a 50
        # 3 for a miss
        self.replay = []

    def set_map_id(self, map_id):
        self.map_id = map_id

    def load_map(self):
        filename = "data/{}.osu".format(self.map_id)

        self.map = Map(filename)
        self.map.parse_file()

        self.hit_window50 = 150 + 50 * (5 - self.map.overall_difficulty) / 5
        self.hit_window100 = 100 + 40 * (5 - self.map.overall_difficulty) / 5
        self.hit_window300 = 50 + 30 * (5 - self.map.overall_difficulty) / 5

    def load_replay(self, player_id):
        replay_data = download_replay(self.api_key, player_id, self.map_id)

        total_time = 0
        obj_idx = 0
        l_click = False
        r_click = False
        for replay_event in replay_data:
            time = replay_event.time_since_previous_action
            if time < 0:
                continue
            x = replay_event.x
            y = replay_event.y
            key = replay_event.keys_pressed

            # Checks which keys were pressed at which timestamp.
            k5 = key & 5 == 5
            k10 = key & 10 == 10

            on_l_click = k5 and not l_click
            on_r_click = k10 and not r_click

            l_click = k5
            r_click = k10

            total_time += time

            # If a key was pressed, check if there is a hitobject within timeframe.
            if obj_idx >= len(self.map.hit_objects):
                continue

            hit_time = abs(total_time - self.map.hit_objects[obj_idx][0])
            if (on_r_click or on_l_click) and hit_time < self.hit_window50:
                if type(self.map.hit_objects[obj_idx][1]) is Circle:
                    # Actually clicking on the circle.
                    if (x - self.map.hit_objects[obj_idx][1].x)**2 + (y - self.map.hit_objects[obj_idx][1].y)**2 \
                            < (54.4 - 4.48 * self.map.circle_size)**2:

                        if hit_time < self.hit_window300:
                            pass
                        elif hit_time < self.hit_window100:
                            print("A 100 at circle: {}".format(obj_idx))
                        else:
                            print("A 50")

                    else:
                        print("Missed circle: {}.".format(obj_idx))
                else:
                    if (x - self.map.hit_objects[obj_idx][1].x)**2 + (y - self.map.hit_objects[obj_idx][1].y)**2\
                            < (54.4 - 4.48 * self.map.circle_size)**2:

                        pass

                    else:
                        print("Missed slider: {}.".format(obj_idx))
                obj_idx += 1
        return


def analyze(api_key, name, map_id):
    map_replay = MapReplay(api_key)

    map_replay.set_map_id(map_id)
    map_replay.load_map()
    map_replay.load_replay(name)
