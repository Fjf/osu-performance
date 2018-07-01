class Circle:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Slider:
    def __init__(self, x, y, sliderdata):
        self.x = x
        self.y = y
        spl = sliderdata.split("|")
        self.type = spl[0]
        # We need this to later calculate if the player stayed on the slider
        if self.type == "L":
            self.end_x = spl[1].split(":")[0]
            self.end_y = spl[1].split(":")[1]
            pass
        elif self.type == "P":
            pass
        elif self.type == "B":
            pass
        self.sliderdata = spl[1]