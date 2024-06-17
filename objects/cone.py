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

        self.vbo_vertices = glGenBuffers(1)
        self.vbo_faces = glGenBuffers(1)

        self.init_vbo()

    def generate_vertices(self):
        vertices = [(0, 0, 0)]  # Center of base
        angle_increment = 2 * np.pi / self.slices
        for i in range(self.slices):
            angle = i * angle_increment
            x = self.base_radius * np.cos(angle)
            z = self.base_radius * np.sin(angle)
            vertices.append((x, 0, z))
        vertices.append((0, self.height, 0))  # Apex of the cone
        return np.array(vertices, dtype=np.float32)

    def generate_faces(self):
        faces = []
        for i in range(1, self.slices):
            faces.append((0, i, i+1))
        faces.append((0, self.slices, 1))  # Last face connecting to the first vertex

        apex_index = len(self.vertices) - 1
        for i in range(1, self.slices):
            faces.append((apex_index, i, i+1))
        faces.append((apex_index, self.slices, 1))  # Last side face
        return np.array(faces, dtype=np.uint32)

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
        
        glEnableClientState(GL_VERTEX_ARRAY)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glDrawElements(GL_TRIANGLES, len(self.faces) * 3, GL_UNSIGNED_INT, None)
        
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
