import os

from downloaders.map_downloader import MapDownloader
from downloaders.replay_downloader import decode_file
from replayanalyzer.mapreplay import analyze

if __name__ == "__main__":
    # Create folder for data if it doesnt exist yet.
    if not os.path.isdir("data/"):
        os.mkdir("data")

    # Read keys from file
    with open('key', 'r') as f:
        keys = f.readlines()
    keys = [x.strip() for x in keys]

    # decode_file("2_in_1_men", "123456789")

    map_id = "123456789"
    map_downloader = MapDownloader(keys[2], keys[3])
    map_downloader.download(map_id)

    analyze(keys[1], "2_in_1_men", map_id)