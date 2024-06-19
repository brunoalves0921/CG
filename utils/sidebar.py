import pygame
from OpenGL.GL import *

class Sidebar:
    def __init__(self):
        self.buttons = [
            {'label': 'Cubo', 'action': 'cube'},
            {'label': 'Esfera', 'action': 'sphere'},
            {'label': 'Cone', 'action': 'cone'},
            {'label': 'Cilindro', 'action': 'cylinder'},
            {'label': 'Meia Esfera', 'action': 'halfsphere'},
            {'label': 'Pirâmide', 'action': 'pyramid'}
        ]
        self.width = 200
        self.height = 50
        self.spacing = 10
        self.start_x = 10
        self.start_y = 100  # Ajustado para começar mais abaixo

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 18)

        self.visible = True  # Inicialmente a sidebar está visível

    def draw(self):
        if self.visible:
            for i, button in enumerate(self.buttons):
                y = self.start_y + i * (self.height + self.spacing)
                self.draw_button(self.start_x, y, self.width, self.height, button['label'])

    def draw_button(self, x, y, width, height, label):
        self.render_text(label, x + width // 2, y + height // 2)
        glColor3f(0.7, 0.7, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

    def render_text(self, text, x, y, font_name='Arial', font_size=18):
        font = pygame.font.SysFont(font_name, font_size)
        text_surface = font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 0))
        text_data = pygame.image.tostring(text_surface, 'RGBA', True)
        width, height = text_surface.get_size()

        glRasterPos2f(x, y)
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def check_click(self, x, y):
        if not self.visible:
            return None
        
        for i, button in enumerate(self.buttons):
            button_y = self.start_y + i * (self.height + self.spacing)
            if (self.start_x <= x <= self.start_x + self.width and 
                button_y <= y <= button_y + self.height):
                return button['action']
        return None

    def toggle_visibility(self):
        self.visible = not self.visible
