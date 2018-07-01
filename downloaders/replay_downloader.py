import base64
import json
import os
import pickle
from typing import List

import requests
from osrparse import parse_replay_file
from osrparse.replay import Replay, ReplayEvent


def download_replay(api_key, player_id, map_id) -> List[ReplayEvent]:
    # If the replay is already downloaded, dont download again to save
    #  peppy's server.
    filename = "data/{}_{}".format(map_id, player_id)
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            play_data = pickle.load(f)
    else:
        url = "https://osu.ppy.sh/api/get_replay?k={}&m=0&b={}&u={}".format(api_key, map_id, player_id)
        print("Requesting Replay Data...")

        r = requests.get(url)
        json_data = json.loads(r.text)

        replay_data = base64.b64decode(json_data["content"])
        play_data = Replay.parse_play_data(replay_data)
        with open(filename, 'wb') as f:
            pickle.dump(play_data, f, pickle.HIGHEST_PROTOCOL)

    return play_data


def decode_file(player_id, map_id):
    filename = "data/{}_{}".format(map_id, player_id)
    data = parse_replay_file(filename)
    with open(filename, 'wb') as f:
        pickle.dump(data.play_data, f, pickle.HIGHEST_PROTOCOL)
