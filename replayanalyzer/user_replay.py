from os import listdir
import os
from os.path import isfile, join

from downloaders.replay_downloader import decode_file


def parse_user_replays():
    """
    Will iterate over all files in the data/file_replay_data folder and convert them all to pickle objects.
    These pickle objects will contain data for each hit object in the map.

    Parsed files will be moved to data/
    :return:
    """

    path = "data/file_replay_data"
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for file in files:
        with open(file, "r"):
            # TODO: Read the correct names from the replay data.
            decode_file("2_in_1_men", "123456789")
        os.remove("{}/{}".format(path, file))
