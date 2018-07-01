

class Map:
    def __init__(self, file_url):
        self.file = self._get_file(file_url)
        self.hit_objects = None
        self.difficulty = None

    def parse_file(self):
        self._parse_hit_objects()

    @staticmethod
    def _get_file(file_url):
        with open(file_url, "r") as f:
            return f.read()

    def _parse_hit_objects(self):
        data = self.file.split("\n\n")
        for d in data:
            print(d)
        # self.difficulty = MapDifficulty()


map = Map("E:/Projects/osu-performance/data/123456789.osu")
map.parse_file()