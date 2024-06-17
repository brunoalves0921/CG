from objects import Object
from OpenGL.GL import *
import numpy as np

class Pyramid(Object):
    def __init__(self, base_length=2, height=2):
        super().__init__([0, 0, 0])
        self.selected = False
        self.base_length = base_length
        self.height = height
        self.scale_factor = [1.0, 1.0, 1.0]

        self.vertices = np.array(self.generate_vertices(), dtype=np.float32)
        self.faces = np.array(self.generate_faces(), dtype=np.uint32)

        # VBO IDs
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_faces = glGenBuffers(1)

        self.init_vbo()

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
            (0, 1, 2),  # Base faces split into two triangles
            (0, 2, 3)
        ]
        return faces

    def init_vbo(self):
        # Upload vertices to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Upload faces to VBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

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
        
        # Desenhar faces da pirâmide
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        
        # Desenhar faces laterais (triângulos)
        for i in range(4):
            glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, ctypes.c_void_p(i * 3 * 4))
        
        # Desenhar faces da base (dois triângulos)
        for i in range(4, 6):
            glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, ctypes.c_void_p(i * 3 * 4))

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
