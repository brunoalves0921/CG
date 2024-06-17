from objects import Object
from OpenGL.GL import *
import numpy as np

class Cylinder(Object):
    def __init__(self, radius=1, height=2, slices=20):
        super().__init__([0, 0, 0])
        self.selected = False
        self.radius = radius
        self.height = height
        self.slices = slices
        self.scale_factor = [1.0, 1.0, 1.0]

        self.vertices, self.faces = self.generate_geometry()

    def generate_geometry(self):
        vertices = []
        faces = []

        # Generate vertices for the top and bottom circles
        for j in [0, self.height]:
            for i in range(self.slices):
                angle = 2 * np.pi * i / self.slices
                x = self.radius * np.cos(angle)
                z = self.radius * np.sin(angle)
                y = j
                vertices.append((x, y, z))

        # Add center vertices for the top and bottom circles
        vertices.append((0, 0, 0))          # Bottom center
        vertices.append((0, self.height, 0))  # Top center

        # Generate faces for the side
        for i in range(self.slices):
            next_i = (i + 1) % self.slices
            bottom_current = i
            bottom_next = next_i
            top_current = i + self.slices
            top_next = next_i + self.slices
            faces.append((bottom_current, bottom_next, top_next, top_current))

        # Generate faces for the top and bottom circles
        bottom_center_index = 2 * self.slices
        top_center_index = 2 * self.slices + 1
        for i in range(self.slices):
            next_i = (i + 1) % self.slices
            faces.append((bottom_center_index, i, next_i))              # Bottom face
            faces.append((top_center_index, top_next, top_current))  # Top face

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
        
        # Draw side faces
        glBegin(GL_QUADS)
        for face in self.faces[:-2 * self.slices]:
            for vertex in face:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        
        # Draw top and bottom faces
        glBegin(GL_TRIANGLES)
        for face in self.faces[-2 * self.slices:]:
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
