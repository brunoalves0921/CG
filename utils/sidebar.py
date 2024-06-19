import pygame
from OpenGL.GL import *
import OpenGL.GLUT as glut
from math import cos, sin

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
        self.hovered_button = None

    def draw(self):
        if self.visible:
            for i, button in enumerate(self.buttons):
                y = self.start_y + i * (self.height + self.spacing)
                is_hovered = (i == self.hovered_button)
                self.draw_button(self.start_x, y, self.width, self.height, button['label'], is_hovered)

    def draw_button(self, x, y, width, height, label, is_hovered):
        if is_hovered:
            glColor3f(0.5, 0.5, 0.5)  # Cor mais escura para hover
        else:
            glColor3f(0.7, 0.7, 0.7)  # Cor padrão

        self.render_text(label, x + width // 2, y + height // 2)
        
        # Desenha o botão com bordas arredondadas
        self.draw_rounded_rect(x, y, width, height, 10)

    def draw_rounded_rect(self, x, y, width, height, radius):
        segments = 16
        glBegin(GL_POLYGON)
        for i in range(segments):
            theta = 2.0 * 3.1415926 * i / segments
            dx = radius * cos(theta)
            dy = radius * sin(theta)
            glVertex2f(x + radius + dx, y + radius + dy)
            glVertex2f(x + width - radius + dx, y + radius + dy)
            glVertex2f(x + width - radius + dx, y + height - radius + dy)
            glVertex2f(x + radius + dx, y + height - radius + dy)
        glEnd()

    def render_text(self, text, x, y, font_name='Arial', font_size=18):
        font = pygame.font.SysFont(font_name, font_size)
        text_surface = font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 0))
        text_data = pygame.image.tostring(text_surface, 'RGBA', True)
        width, height = text_surface.get_size()

        # Centralizar o texto e ajustar a posição vertical
        text_y_offset = -16  # Ajuste vertical para centralizar o texto
        glRasterPos2f(x - width // 2, y - height // 2 - text_y_offset)
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

    def update_hover(self, mouse_x, mouse_y):
        if not self.visible:
            self.hovered_button = None
            return

        for i, button in enumerate(self.buttons):
            button_y = self.start_y + i * (self.height + self.spacing)
            if (self.start_x <= mouse_x <= self.start_x + self.width and 
                button_y <= mouse_y <= button_y + self.height):
                self.hovered_button = i
                return
        self.hovered_button = None

    def toggle_visibility(self):
        self.visible = not self.visible
