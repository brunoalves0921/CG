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

    def set_preset_position(self, preset):
        if preset == 1:
            # Posição frontal padrão, olhando para a origem (0, 0, 0)
            self.position = [0, 0, -5] 
            self.rotation = [0, 0]  
        elif preset == 2:
            # Posição lateral direita, olhando para a origem
            self.position = [0, 0, -5]  
            self.rotation = [0, -90] 
            self.zoom = -20
        elif preset == 3:
            # Posição lateral direita, olhando para a origem
            self.position = [0, 0, -5]
            self.rotation = [0, 180]  
            self.zoom = -20  
        elif preset == 4:
            # Posição lateral esquerda, olhando para a origem
            self.position = [0, 0, -5]  
            self.rotation = [0, 90] 
            self.zoom = -20  
        elif preset == 5:
            # Posição superior, olhando para a origem
            self.position = [0, 0, 0]  
            self.rotation = [90, 0] 
            self.zoom = -20
        elif preset == 6:
            # Posição inferior, olhando para a origem
            self.position = [0, 0, -5]  
            self.rotation = [-90, 0] 
            self.zoom = -20 
