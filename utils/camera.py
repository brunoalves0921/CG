class Camera:
    def __init__(self):
        self.rotation = [0, 0]  # Rotação inicial da câmera nos eixos X e Y
        self.zoom = -20  # Zoom inicial da câmera
        self.position = [0, 0, 0]  # Posição inicial da câmera no espaço tridimensional
        

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
