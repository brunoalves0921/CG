from objects import Object
from OpenGL.GL import *
import numpy as np

class HalfSphere(Object):
    def __init__(self, radius=1, stacks=20, slices=20):
        super().__init__([0, 0, 0])
        self.selected = False
        self.radius = radius
        self.stacks = stacks
        self.slices = slices
        self.scale_factor = [1.0, 1.0, 1.0]

        self.vertices, self.faces = self.generate_geometry()

    def generate_geometry(self):
        vertices = []
        faces = []

        for i in range(self.stacks + 1):
            theta = (i / self.stacks) * (np.pi / 2)
            for j in range(self.slices + 1):
                phi = (j / self.slices) * (2 * np.pi)
                x = self.radius * np.sin(theta) * np.cos(phi)
                y = self.radius * np.sin(theta) * np.sin(phi)
                z = self.radius * np.cos(theta)
                vertices.append((x, y, z))

        for i in range(self.stacks):
            for j in range(self.slices):
                first = i * (self.slices + 1) + j
                second = first + self.slices + 1
                faces.append((first, second, first + 1))
                faces.append((second, second + 1, first + 1))

        return vertices, faces

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        
        glRotatef(self.transform.rotation[0], 1, 0, 0)
        glRotatef(self.transform.rotation[1], 0, 1, 0)
        glRotatef(self.transform.rotation[2], 0, 0, 1)

        glScalef(*self.scale_factor)
        
        if self.selected:
            glColor3f(1.0, 0.5, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)
        
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex in face:
                glVertex3fv(self.vertices[vertex])
        glEnd()

        glPopMatrix()

    def rotate(self, angle, axis):
        if axis == (1, 0, 0):
            self.transform.rotation[0] += angle
        elif axis == (0, 1, 0):
            self.transform.rotation[1] += angle
        elif axis == (0, 0, 1):
            self.transform.rotation[2] += angle

    def scale(self, factor, axis):
        min_scale = 0.1
        if axis == (1, 0, 0):
            new_scale = max(min_scale, self.scale_factor[0] + factor)
            self.scale_factor[0] = new_scale
        elif axis == (0, 1, 0):
            new_scale = max(min_scale, self.scale_factor[1] + factor)
            self.scale_factor[1] = new_scale
        elif axis == (0, 0, 1):
            new_scale = max(min_scale, self.scale_factor[2] + factor)
            self.scale_factor[2] = new_scale

    def translate(self, distance, axis):
        if axis == (1, 0, 0):
            self.position[0] += distance
        elif axis == (0, 1, 0):
            self.position[1] += distance
        elif axis == (0, 0, 1):
            self.position[2] += distance

    def shear(self, shear_factor, plane):
        pass