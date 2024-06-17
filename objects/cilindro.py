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

        self.vertices, self.side_faces, self.top_bottom_faces = self.generate_geometry()

        # Convertendo os dados para numpy arrays
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.side_faces = np.array(self.side_faces, dtype=np.uint32)
        self.top_bottom_faces = np.array(self.top_bottom_faces, dtype=np.uint32)

        # VBO IDs
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_side_faces = glGenBuffers(1)
        self.vbo_top_bottom_faces = glGenBuffers(1)

        self.init_vbo()

    def generate_geometry(self):
        vertices = []
        side_faces = []
        top_bottom_faces = []

        for j in [0, self.height]:
            for i in range(self.slices):
                angle = 2 * np.pi * i / self.slices
                x = self.radius * np.cos(angle)
                z = self.radius * np.sin(angle)
                y = j
                vertices.append((x, y, z))

        bottom_center_index = len(vertices)
        vertices.append((0, 0, 0))
        top_center_index = len(vertices)
        vertices.append((0, self.height, 0))

        for i in range(self.slices):
            next_i = (i + 1) % self.slices
            bottom_current = i
            bottom_next = next_i
            top_current = i + self.slices
            top_next = next_i + self.slices
            side_faces.append((bottom_current, bottom_next, top_next, top_current))
            top_bottom_faces.append((bottom_center_index, i, next_i))
            top_bottom_faces.append((top_center_index, top_next, top_current))

        return vertices, side_faces, top_bottom_faces

    def init_vbo(self):
        # Upload vertices to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Upload side faces to VBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_side_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.side_faces.nbytes, self.side_faces, GL_STATIC_DRAW)

        # Upload top and bottom faces to VBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_top_bottom_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.top_bottom_faces.nbytes, self.top_bottom_faces, GL_STATIC_DRAW)

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

        # Desenhar faces laterais
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_side_faces)
        glDrawElements(GL_QUADS, len(self.side_faces) * 4, GL_UNSIGNED_INT, None)

        # Desenhar faces superior e inferior
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_top_bottom_faces)
        glDrawElements(GL_TRIANGLES, len(self.top_bottom_faces) * 3, GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)

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
