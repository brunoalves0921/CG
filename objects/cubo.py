from objects import Object
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class Cube(Object):
    base_vertices = (
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
        self.vertices = [list(vertex) for vertex in Cube.base_vertices]  # Converter para listas mutáveis

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
                glVertex3fv(self.vertices[vertex])
        glEnd()

        # Desenhar arestas do cubo
        glColor3f(0, 0, 0)
        glBegin(GL_LINES)
        for edge in Cube.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
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

    def shear(self, shear_factor, plane): #Função para aplicar cisalhamento ao cubo.
        shear_matrix = np.identity(4)
        if plane == 'xy':
            shear_matrix[0][1] = shear_factor  # Shear X based on Y
        elif plane == 'yx':
            shear_matrix[1][0] = shear_factor # Shear Y based on X
        elif plane == 'xz':
            shear_matrix[0][2] = shear_factor
        elif plane == 'zx':
            shear_matrix[2][0] = shear_factor

        # Apply shear only to the vertices that are not fixed
        new_vertices = []
        for vertex in self.vertices:
            v = np.array(vertex + [1])
            # Apply shear to the vertices on the positive side of the fixed plane
            if (plane in ['xy', 'xz'] and vertex[1] >= 0) or \
               (plane in ['yx', 'yz'] and vertex[0] >= 0) or \
               (plane in ['zx', 'zy'] and vertex[2] >= 0):
                v_new = shear_matrix @ v
                new_vertices.append(list(v_new[:3]))
            else:
                new_vertices.append(vertex)
        
        self.vertices = new_vertices
