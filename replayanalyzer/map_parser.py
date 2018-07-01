from replayanalyzer.objects import Circle, Slider


class Map:
    def __init__(self, file_url):
        self.file = self._get_file(file_url)

        self._raw_hit_objects = None
        self._raw_diff_data = None

        self.hit_objects = []
        self.drain_rate = -1
        self.circle_size = -1
        self.overall_difficulty = -1
        self.approach_rate = -1
        self.slider_multiplier = -1
        self.slider_tick_rate = -1

    def parse_file(self):
        self._parse_data()
        self._parse_hit_objects()
        self._parse_difficulty()

    @staticmethod
    def _get_file(file_url):
        with open(file_url, "r") as f:
            return f.read()

    def _parse_data(self):
        data = self.file.split("\n[")

        data = [segment.strip().split("]\n") for segment in data]

        if data[0][0] != "osu file format v14":
            raise Exception("Unsupported osu map version.")

        for header, lines in data[1:]:
            if header == "HitObjects":
                self._raw_hit_objects = lines
            elif header == "Difficulty":
                self._raw_diff_data = lines

    def _parse_hit_objects(self):
        lines = [line.strip() for line in self._raw_hit_objects.split("\n")]

        self.hit_objects = []
        for line in lines:
            obj_data = line.split(",")

            x = int(obj_data[0])
            y = int(obj_data[1])
            time = int(obj_data[2])
            obj_type = int(obj_data[3])
            if obj_type % 4 == 1:  # %4, to also catch the circles that start new combo
                self.hit_objects.append((time, Circle(x, y)))
            elif obj_type % 4 == 2:  # %4, to also catch the sliders that start new combo
                self.hit_objects.append((time, Slider(x, y, obj_data[5])))

    def _parse_difficulty(self):
        lines = [line.strip() for line in self._raw_diff_data.split("\n")]

        for line in lines:
            setting, value = line.split(":")
            if setting == "HPDrainRate":
                self.drain_rate = float(value)
            elif setting == "CircleSize":
                self.circle_size = float(value)
            elif setting == "OverallDifficulty":
                self.overall_difficulty = float(value)
            elif setting == "ApproachRate":
                self.approach_rate = float(value)
            elif setting == "SliderMultiplier":
                self.slider_multiplier = float(value)
            elif setting == "SliderTickRate":
                self.slider_tick_rate = float(value)
