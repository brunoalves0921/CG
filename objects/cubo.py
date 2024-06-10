from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class Cube:
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
        self.scale_factors = [1, 1, 1]
        self.rotation_angles = [0, 0, 0]
        self.position = [0, 0, 0]
        self.selected = False

    def draw(self): #Função para desenhar o cubo.
        glPushMatrix()
        glTranslatef(*self.position)
        
        glRotatef(self.rotation_angles[0], 1, 0, 0)
        glRotatef(self.rotation_angles[1], 0, 1, 0)
        glRotatef(self.rotation_angles[2], 0, 0, 1)

        glScalef(*self.scale_factors)
        
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
            self.rotation_angles[0] += angle
        elif axis == (0, 1, 0):
            self.rotation_angles[1] += angle
        elif axis == (0, 0, 1):
            self.rotation_angles[2] += angle

    def scale(self, factor, axis): #Função para escalar o cubo em um eixo específico.
        if axis == (1, 0, 0):
            self.scale_factors[0] = max(0.1, self.scale_factors[0] + factor)
        elif axis == (0, 1, 0):
            self.scale_factors[1] = max(0.1, self.scale_factors[1] + factor)
        elif axis == (0, 0, 1):
            self.scale_factors[2] = max(0.1, self.scale_factors[2] + factor)

    def translate(self, distance, axis): #Função para transladar o cubo em um eixo específico.
        if axis == (1, 0, 0):
            self.position[0] += distance
        elif axis == (0, 1, 0):
            self.position[1] += distance
        elif axis == (0, 0, 1):
            self.position[2] += distance

    def intersects(self, ray_origin, ray_direction): #
        # Ajustar os limites para considerar a posição e escala do cubo
        min_bounds = np.array(self.position) - np.array(self.scale_factors)
        max_bounds = np.array(self.position) + np.array(self.scale_factors)

        t_min = -np.inf
        t_max = np.inf

        for i in range(3):
            if abs(ray_direction[i]) < 1e-8:
                if ray_origin[i] < min_bounds[i] or ray_origin[i] > max_bounds[i]:
                    return False
            else:
                t1 = (min_bounds[i] - ray_origin[i]) / ray_direction[i]
                t2 = (max_bounds[i] - ray_origin[i]) / ray_direction[i]
                t_min = max(t_min, min(t1, t2))
                t_max = min(t_max, max(t1, t2))
                if t_max < t_min:
                    return False

        return True
