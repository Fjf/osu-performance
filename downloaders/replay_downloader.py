import base64
import json
import lzma
import os

import requests


def download_replay(api_key, player_id, map_id):
    # If the replay is already downloaded, dont download again to save
    #  peppy's server.
    filename = "data/{}_{}".format(map_id, player_id)
    if os.path.isfile(filename):
        with open(filename, 'r', encoding="utf-8") as file:
            replay_data = file.read()
    else:
        url = "https://osu.ppy.sh/api/get_replay?k={}&m=0&b={}&u={}".format(api_key, map_id, player_id)
        print("Requesting Replay Data...")

        r = requests.get(url)
        json_data = json.loads(r.text)

        data = base64.b64decode(json_data["content"])
        replay_data = lzma.decompress(data).decode("utf-8")
        with open(filename, 'w') as f:
            f.write(replay_data)

    return replay_data
