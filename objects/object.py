from utils.transform import Transform


class Object:
    def __init__(self, position):
        self.transform = Transform()
        self.position = position

    def draw(self):
        pass

    def rotate(self, angle, axis):
        pass

    def translate(self, distance, direction):
        pass 

    def scale(self, factor, axis):
        pass
