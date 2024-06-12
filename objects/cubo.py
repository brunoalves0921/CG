from objects import Object
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class Cube(Object):
    vertices = (
        (1, -1, -1),  # 0
        (1, 1, -1),
        (-1, 1, -1),
        (-1, -1, -1),  # 3
        (1, -1, 1),
        (1, 1, 1),
        (-1, -1, 1),
        (-1, 1, 1)  # 7
    )

    edges = (
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 7),
        (7, 6),
        (6, 4),
        (0, 4),
        (1, 5),
        (2, 7),
        (3, 6)
    )

    faces = (
        (0, 1, 2, 3),
        (3, 2, 7, 6),
        (6, 7, 5, 4),
        (4, 5, 1, 0),
        (1, 5, 7, 2),
        (4, 0, 3, 6)
    )

    def __init__(self):
        super().__init__([0, 0, 0])
        self.selected = False

    def draw(self): #Função para desenhar o cubo.
        glPushMatrix()
        glTranslatef(*self.position)
        
        glRotatef(self.transform.rotation[0], 1, 0, 0)
        glRotatef(self.transform.rotation[1], 0, 1, 0)
        glRotatef(self.transform.rotation[2], 0, 0, 1)

        glScalef(*self.transform.scale)
        
        # Definir cor do cubo se selecionado ou não
        if self.selected:
            glColor3f(1.0, 0.5, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)
        
        # Desenhar faces do cubo
        glBegin(GL_QUADS)
        for face in Cube.faces:
            for vertex in face:
                glVertex3fv(Cube.vertices[vertex])
        glEnd()

        # Desenhar arestas do cubo
        glColor3f(0, 0, 0)
        glBegin(GL_LINES)
        for edge in Cube.edges:
            for vertex in edge:
                glVertex3fv(Cube.vertices[vertex])
        glEnd()

        glPopMatrix()

    def rotate(self, angle, axis): #Função para rotacionar o cubo em um eixo específico.
        if axis == (1, 0, 0):
            self.transform.rotation[0] += angle
        elif axis == (0, 1, 0):
            self.transform.rotation[1] += angle
        elif axis == (0, 0, 1):
            self.transform.rotation[2] += angle

    def scale(self, factor, axis): #Função para escalar o cubo em um eixo específico.
        if axis == (1, 0, 0):
            self.transform.scale[0] = max(0.001, self.transform.scale[0] + factor)
        elif axis == (0, 1, 0):
            self.transform.scale[1] = max(0.001, self.transform.scale[1] + factor)
        elif axis == (0, 0, 1):
            self.transform.scale[2] = max(0.001, self.transform.scale[2] + factor)

    def translate(self, distance, axis): #Função para transladar o cubo em um eixo específico.
        if axis == (1, 0, 0):
            self.position[0] += distance
        elif axis == (0, 1, 0):
            self.position[1] += distance
        elif axis == (0, 0, 1):
            self.position[2] += distance
