import os

from downloaders.map_downloader import MapDownloader
from replayanalyzer.map_replay import analyze
from replayanalyzer.user_replay import parse_user_replays

if __name__ == "__main__":
    # Create folder for data if it doesnt exist yet.
    if not os.path.isdir("data/"):
        os.mkdir("data")

    # Read keys from file
    with open('key', 'r') as f:
        keys = f.readlines()
    keys = [x.strip() for x in keys]

    # Will look in the folder data/file_replay_data for user replays and parse them.
    parse_user_replays()

    map_id = "1368008"
    map_downloader = MapDownloader(keys[2], keys[3])
    map_downloader.download(map_id)

    analyze(keys[1], "2_in_1_men", map_id)