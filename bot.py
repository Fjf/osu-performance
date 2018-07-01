import sys
import os

from downloaders.map_downloader import MapDownloader
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

    map_downloader = MapDownloader(keys[2], keys[3])

    map_id = "1531044"
    map_downloader.download(map_id)

    analyze(keys[1], "naam", map_id)