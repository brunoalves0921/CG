from objects import Object
from OpenGL.GL import *
import numpy as np

class Pyramid(Object):
    def __init__(self, base_length=1, height=2):
        super().__init__([0, 0, 0])
        self.selected = False
        self.base_length = base_length
        self.height = height
        self.scale_factor = [1.0, 1.0, 1.0]

        self.vertices = self.generate_vertices()
        self.faces = self.generate_faces()

    def generate_vertices(self):
        half_base = self.base_length / 2
        vertices = [
            (-half_base, 0, -half_base),  # Base vertices
            (half_base, 0, -half_base),
            (half_base, 0, half_base),
            (-half_base, 0, half_base),
            (0, self.height, 0)  # Apex
        ]
        return vertices

    def generate_faces(self):
        faces = [
            (0, 1, 4),  # Side faces
            (1, 2, 4),
            (2, 3, 4),
            (3, 0, 4),
            (0, 1, 2, 3)  # Base face
        ]
        return faces

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
        for face in self.faces[:-1]:  # Draw side faces
            for vertex in face:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        
        glBegin(GL_QUADS)
        for vertex in self.faces[-1]:  # Draw base face
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
