import os

import requests


class MapDownloader:
    def __init__(self, user, password):
        data = {
            "autologin": "on",
            "login": "login",
            "password": password,
            "username": user,
            "redirect": "",
            "sid": ""
        }
        res = requests.post("https://osu.ppy.sh/forum/ucp.php?mode=login", data)
        self.is_logged_in = res.status_code == 200

    def download(self, map_id):
        if not self.is_logged_in:
            return False

        filename = "data/{}.osu".format(map_id)

        if os.path.isfile(filename):
            return True

        res = requests.get("https://osu.ppy.sh/osu/{}".format(map_id))

        with open(filename, mode="w", newline="", encoding="utf8") as file:
            file.write(res.text)

        return True
