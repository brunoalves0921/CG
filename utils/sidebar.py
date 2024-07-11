import pygame
import tkinter as tk
import OpenGL.GLUT as glut
from tkinter import filedialog
from OpenGL.GL import *
from objects import Cube, Sphere, Mesh  # Certifique-se de importar a classe Mesh
from math import cos, sin, pi

class Sidebar:
    def __init__(self):
        self.buttons = [
            {'label': 'Cubo', 'action': 'cube'},
            {'label': 'Esfera', 'action': 'sphere'},
            {'label': 'Cone', 'action': 'cone'},
            {'label': 'Cilindro', 'action': 'cylinder'},
            {'label': 'Meia Esfera', 'action': 'halfsphere'},
            {'label': 'Pirâmide', 'action': 'pyramid'},
            {'label': 'Luz', 'action': 'light'},
            {'label': 'Adicionar Textura', 'action': 'add_texture'},
            {'label': 'Adicionar OBJ', 'action': 'add_obj'}  # Novo botão para adicionar .obj
        ]
        self.width = 200
        self.height = 50
        self.spacing = 10
        self.start_x = 10
        self.start_y = 100

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 18)
        self.textures = self.create_textures()  # Criar texturas de texto

        self.visible = True
        self.hovered_button = None

    def create_textures(self):
        textures = []
        for button in self.buttons:
            text_surface = self.font.render(button['label'], True, (255, 255, 255, 255), (0, 0, 0, 0))
            text_data = pygame.image.tostring(text_surface, 'RGBA', True)
            width, height = text_surface.get_size()
            textures.append((text_data, width, height))
        return textures

    def draw(self):
        if not self.visible:
            return

        glPushAttrib(GL_ALL_ATTRIB_BITS)  # Salvar o estado atual do OpenGL

        glDisable(GL_LIGHTING)  # Desativar a iluminação
        glDisable(GL_DEPTH_TEST)  # Desativar o teste de profundidade

        for i, button in enumerate(self.buttons):
            y = self.start_y + i * (self.height + self.spacing)
            is_hovered = (i == self.hovered_button)
            self.draw_button(self.start_x, y, self.width, self.height, button['label'], is_hovered)

        self.draw_texts()

        glEnable(GL_DEPTH_TEST)  # Reativar o teste de profundidade
        glEnable(GL_LIGHTING)  # Reativar a iluminação

        glPopAttrib()  # Restaurar o estado do OpenGL

    def draw_button(self, x, y, width, height, label, is_hovered):
        glColor3f(0.5, 0.5, 0.5) if is_hovered else glColor3f(0.7, 0.7, 0.7)
        self.draw_rounded_rect(x, y, width, height, 10)

    def draw_rounded_rect(self, x, y, width, height, radius):
        segments = 16

        glBegin(GL_TRIANGLE_FAN)
        for i in range(segments):
            theta = 2.0 * pi * i / segments
            dx = radius * cos(theta)
            dy = radius * sin(theta)
            glVertex2f(x + radius + dx, y + height - radius + dy)
            glVertex2f(x + width - radius + dx, y + height - radius + dy)
            glVertex2f(x + width - radius + dx, y + radius + dy)
            glVertex2f(x + radius + dx, y + radius + dy)
        glEnd()

        glBegin(GL_QUADS)
        glVertex2f(x + radius, y + height)
        glVertex2f(x + width - radius, y + height)
        glVertex2f(x + width - radius, y + height - radius)
        glVertex2f(x + radius, y + height - radius)
        glVertex2f(x + radius, y)
        glVertex2f(x + width - radius, y)
        glVertex2f(x + width - radius, y + radius)
        glVertex2f(x + radius, y + radius)
        glVertex2f(x, y + radius)
        glVertex2f(x + radius, y + radius)
        glVertex2f(x + radius, y + height - radius)
        glVertex2f(x, y + height - radius)
        glVertex2f(x + width - radius, y + radius)
        glVertex2f(x + width, y + radius)
        glVertex2f(x + width, y + height - radius)
        glVertex2f(x + width - radius, y + height - radius)
        glEnd()

    def draw_texts(self):
        for i, (text_data, width, height) in enumerate(self.textures):
            y = self.start_y + i * (self.height + self.spacing)
            x = self.start_x + self.width // 2
            text_y = y + self.height // 2
            self.render_text(text_data, x, text_y, width, height)

    def render_text(self, text_data, x, y, width, height):
        text_y_offset = 18  # Ajuste vertical para centralizar o texto
        glRasterPos2f(x - width // 2, y - height // 2 + text_y_offset)
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def check_click(self, x, y, scene):
        if not self.visible:
            return None

        for i, button in enumerate(self.buttons):
            button_y = self.start_y + i * (self.height + self.spacing)
            if self.start_x <= x <= self.start_x + self.width and button_y <= y <= button_y + self.height:
                action = button['action']
                if action == 'add_texture':
                    self.add_texture(scene)
                elif action == 'add_obj':
                    self.add_obj(scene)
                else:
                    return action
        return None

    def add_texture(self, scene):
        selected_object = next((obj for obj in scene.objects if obj.selected), None)
        if selected_object is None:
            print("Nenhum objeto selecionado para adicionar textura.")
            return

        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            selected_object.load_texture(file_path)

    def add_obj(self, scene):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")]
        )
        if file_path:
            new_obj = Mesh(position=[0, 0, 0], filename=file_path, rotation=[0, 0, 0], scale=[1, 1, 1])
            scene.objects.append(new_obj)

    def update_hover(self, mouse_x, mouse_y):
        if not self.visible:
            self.hovered_button = None
            return

        for i, button in enumerate(self.buttons):
            button_y = self.start_y + i * (self.height + self.spacing)
            if self.start_x <= mouse_x <= self.start_x + self.width and button_y <= mouse_y <= button_y + self.height:
                self.hovered_button = i
                return
        self.hovered_button = None

    def toggle_visibility(self):
        self.visible = not self.visible
