from OpenGL.GL import *
from OpenGL.GLU import *

class Cube:
    vertices = (
        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
        (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
    )

    edges = (
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 7), (7, 6), (6, 4),
        (0, 4), (1, 5), (2, 7), (3, 6)
    )

    faces = (
        (0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
        (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)
    )

    def __init__(self):
        pass

    def draw(self):
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

class Sphere:
    def __init__(self, radius=1, slices=16, stacks=16):
        self.radius = radius
        self.slices = slices
        self.stacks = stacks

    def draw(self):
        glColor3f(0.5, 0.5, 0.5)
        quadric = gluNewQuadric()
        gluSphere(quadric, self.radius, self.slices, self.stacks)
        gluDeleteQuadric(quadric)

class Cone:
    def __init__(self, base=1, height=2, slices=16, stacks=16):
        self.base = base
        self.height = height
        self.slices = slices
        self.stacks = stacks

    def draw(self):
        glColor3f(0.5, 0.5, 0.5)
        quadric = gluNewQuadric()
        gluCylinder(quadric, self.base, 0, self.height, self.slices, self.stacks)
        gluDeleteQuadric(quadric)
