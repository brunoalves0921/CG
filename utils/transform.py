class Transform:
    def __init__(self, position=None, rotation=None, scale=None):
        self.position = position if position is not None else [0.0, 0.0, 0.0]
        self.rotation = rotation if rotation is not None else [0.0, 0.0, 0.0]
        self.scale = scale if scale is not None else [1.0, 1.0, 1.0]
