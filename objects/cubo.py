from OpenGL.GL import *
from OpenGL.GLU import *

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
        self.position = [0, 0, 0]  # Adiciona a posição inicial
        self.selected = False  # Adiciona a variável de seleção

    def draw(self):
        glPushMatrix()
        
        # Translade para a posição do cubo
        glTranslatef(*self.position)

        # Aplica as rotações no centro do cubo
        glRotatef(self.rotation_angles[0], 1, 0, 0)
        glRotatef(self.rotation_angles[1], 0, 1, 0)
        glRotatef(self.rotation_angles[2], 0, 0, 1)

        # Depois aplica a escala
        glScalef(*self.scale_factors)
        
        if self.selected:
            glColor3f(1.0, 0.5, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)
        
        glBegin(GL_QUADS)
        for face in Cube.faces:
            for vertex in face:
                glVertex3fv(Cube.vertices[vertex])
        glEnd()

        glColor3f(0, 0, 0)
        glBegin(GL_LINES)
        for edge in Cube.edges:
            for vertex in edge:
                glVertex3fv(Cube.vertices[vertex])
        glEnd()

        glPopMatrix()

    def rotate(self, angle, axis):
        if axis == (1, 0, 0):
            self.rotation_angles[0] += angle
        elif axis == (0, 1, 0):
            self.rotation_angles[1] += angle
        elif axis == (0, 0, 1):
            self.rotation_angles[2] += angle

    def scale(self, factor, axis):
        if axis == (1, 0, 0):
            self.scale_factors[0] += factor
        elif axis == (0, 1, 0):
            self.scale_factors[1] += factor
        elif axis == (0, 0, 1):
            self.scale_factors[2] += factor

    def translate(self, distance, axis):
        if axis == (1, 0, 0):
            self.position[0] += distance
        elif axis == (0, 1, 0):
            self.position[1] += distance
        elif axis == (0, 0, 1):
            self.position[2] += distance
