class Camera:
    def __init__(self):
        self.rotation = [0, 0]
        self.zoom = -20
        self.position = [0, 0, 0]

    def to_dict(self):
        return {
            'rotation': self.rotation,
            'zoom': self.zoom,
            'position': self.position
        }

    def from_dict(self, data):
        self.rotation = data['rotation']
        self.zoom = data['zoom']
        self.position = data['position']
