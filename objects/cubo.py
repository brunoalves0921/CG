from OpenGL.GL import *
from OpenGL.GLU import *

class Cube:
    vertices = (
        (4, -1, -1),  # 0
        (4, 1, -1),
        (-1, 1, -1),
        (-1, -1, -1),  # 3
        (4, -1, 1),
        (4, 1, 1),
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
        pass

    def draw(self):
        glColor3f(0.5, 0.5, 0.5)  # Cor cinza para as faces do cubo
        glBegin(GL_QUADS)
        for face in Cube.faces:
            for vertex in face:
                glVertex3fv(Cube.vertices[vertex])
        glEnd()

        glColor3f(0, 0, 0)  # Cor preta para as arestas do cubo
        glBegin(GL_LINES)
        for edge in Cube.edges:
            for vertex in edge:
                glVertex3fv(Cube.vertices[vertex])
        glEnd()
