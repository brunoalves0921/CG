from objects import Object
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class Sphere(Object):
    def __init__(self, radius=1, subdivisions=3):
        super().__init__([0, 0, 0])
        self.selected = False
        self.radius = radius
        self.vertices, self.faces = self.create_sphere(radius, subdivisions)
        self.vertex_buffer, self.index_buffer = self.setup_buffers()

    def create_sphere(self, radius, subdivisions):
        # Criação do icosaedro inicial
        t = (1.0 + np.sqrt(5.0)) / 2.0

        vertices = [
            [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
            [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
            [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1],
        ]

        faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
        ]

        # Normalizar os vértices para que todos tenham comprimento igual ao raio
        vertices = [self.normalize(np.array(v), radius) for v in vertices]

        # Subdivisão dos triângulos
        for _ in range(subdivisions):
            faces_subdivided = []
            midpoint_cache = {}

            for tri in faces:
                v1, v2, v3 = tri
                a = self.get_midpoint(vertices, v1, v2, midpoint_cache, radius)
                b = self.get_midpoint(vertices, v2, v3, midpoint_cache, radius)
                c = self.get_midpoint(vertices, v3, v1, midpoint_cache, radius)

                faces_subdivided.append((v1, a, c))
                faces_subdivided.append((v2, b, a))
                faces_subdivided.append((v3, c, b))
                faces_subdivided.append((a, b, c))

            faces = faces_subdivided

        return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.uint32)

    def normalize(self, vector, radius):
        norm = np.linalg.norm(vector)
        return vector / norm * radius

    def get_midpoint(self, vertices, v1, v2, midpoint_cache, radius):
        smaller_index = min(v1, v2)
        larger_index = max(v1, v2)
        key = (smaller_index, larger_index)

        if key in midpoint_cache:
            return midpoint_cache[key]

        midpoint = (vertices[v1] + vertices[v2]) / 2
        midpoint = self.normalize(midpoint, radius)
        midpoint_index = len(vertices)
        vertices.append(midpoint)

        midpoint_cache[key] = midpoint_index
        return midpoint_index

    def setup_buffers(self):
        vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

        return vertex_buffer, index_buffer

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        
        glRotatef(self.transform.rotation[0], 1, 0, 0)
        glRotatef(self.transform.rotation[1], 0, 1, 0)
        glRotatef(self.transform.rotation[2], 0, 0, 1)

        glScalef(*self.transform.scale)

        if self.selected:
            glColor3f(1.0, 0.5, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)

        glEnableClientState(GL_VERTEX_ARRAY)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
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
        if axis == (1, 0, 0):
            self.transform.scale[0] = max(0.001, self.transform.scale[0] + factor)
        elif axis == (0, 1, 0):
            self.transform.scale[1] = max(0.001, self.transform.scale[1] + factor)
        elif axis == (0, 0, 1):
            self.transform.scale[2] = max(0.001, self.transform.scale[2] + factor)

    def translate(self, distance, axis):
        if axis == (1, 0, 0):
            self.position[0] += distance
        elif axis == (0, 1, 0):
            self.position[1] += distance
        elif axis == (0, 0, 1):
            self.position[2] += distance

    def shear(self, shear_factor, plane):
        pass  # O cisalhamento pode não ser significativo para esferas, mas pode ser implementado se necessário.
