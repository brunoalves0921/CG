from objects import Object
from OpenGL.GL import *
import numpy as np

class Cone(Object):
    def __init__(self, base_radius=1, height=2, slices=20):
        super().__init__([0, 0, 0])
        self.selected = False
        self.base_radius = base_radius
        self.height = height
        self.slices = slices
        self.scale_factor = [1.0, 1.0, 1.0]

        self.vertices = self.generate_vertices()
        self.faces = self.generate_faces()

    def generate_vertices(self):
        vertices = [(0, 0, 0)]  # Center of base
        angle_increment = 2 * np.pi / self.slices
        for i in range(self.slices):
            angle = i * angle_increment
            x = self.base_radius * np.cos(angle)
            z = self.base_radius * np.sin(angle)
            vertices.append((x, 0, z))
        vertices.append((0, self.height, 0))  # Apex of the cone
        return vertices

    def generate_faces(self):
        faces = []
        for i in range(1, self.slices):
            faces.append((0, i, i+1))
        faces.append((0, self.slices, 1))  # Last face connecting to the first vertex

        apex_index = len(self.vertices) - 1
        for i in range(1, self.slices):
            faces.append((apex_index, i, i+1))
        faces.append((apex_index, self.slices, 1))  # Last side face
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
