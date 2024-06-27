from objects import Object
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image

class Sphere(Object):
    def __init__(self, radius=1, subdivisions=3):
        super().__init__([0, 0, 0])
        self.selected = False
        self.radius = radius
        self.vertices, self.faces, self.uvs = self.create_sphere(radius, subdivisions)
        self.normals = self.calculate_normals()

        self.texture = None
        self.texture_id = None
        self.texture_loaded = False

        self.vbo_vertices = glGenBuffers(1)
        self.vbo_faces = glGenBuffers(1)
        self.vbo_normals = glGenBuffers(1)
        self.vbo_uvs = glGenBuffers(1)  # Novo VBO para coordenadas UV

        self.init_vbo()

    def create_sphere(self, radius, subdivisions):
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

        vertices = [self.normalize(np.array(v), radius) for v in vertices]
        uvs = [self.calculate_uv(vertex) for vertex in vertices]

        for _ in range(subdivisions):
            faces_subdivided = []
            midpoint_cache = {}

            for tri in faces:
                v1, v2, v3 = tri
                a = self.get_midpoint(vertices, uvs, v1, v2, midpoint_cache, radius)
                b = self.get_midpoint(vertices, uvs, v2, v3, midpoint_cache, radius)
                c = self.get_midpoint(vertices, uvs, v3, v1, midpoint_cache, radius)

                faces_subdivided.append((v1, a, c))
                faces_subdivided.append((v2, b, a))
                faces_subdivided.append((v3, c, b))
                faces_subdivided.append((a, b, c))

            faces = faces_subdivided

        return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.uint32), np.array(uvs, dtype=np.float32)

    def normalize(self, vector, radius):
        norm = np.linalg.norm(vector)
        return vector / norm * radius

    def calculate_uv(self, vertex):
        x, y, z = vertex
        u = 0.5 + np.arctan2(z, x) / (2 * np.pi)
        v = 0.5 - np.arcsin(y) / np.pi
        return [u, v]

    def get_midpoint(self, vertices, uvs, v1, v2, midpoint_cache, radius):
        smaller_index = min(v1, v2)
        larger_index = max(v1, v2)
        key = (smaller_index, larger_index)

        if key in midpoint_cache:
            return midpoint_cache[key]

        midpoint = (vertices[v1] + vertices[v2]) / 2
        midpoint = self.normalize(midpoint, radius)
        midpoint_index = len(vertices)
        vertices.append(midpoint)
        uvs.append(self.calculate_uv(midpoint))

        midpoint_cache[key] = midpoint_index
        return midpoint_index

    def load_texture(self, file_path):
        if not self.texture_loaded:
            image = Image.open(file_path)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image_data = np.array(list(image.getdata()), np.uint8)

            if self.texture_id:
                glDeleteTextures([self.texture_id])

            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

            self.texture_loaded = True
            self.texture = file_path

    def init_vbo(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glBufferData(GL_ARRAY_BUFFER, self.uvs.nbytes, self.uvs, GL_STATIC_DRAW)

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

        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glNormalPointer(GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glTexCoordPointer(2, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glDrawElements(GL_TRIANGLES, len(self.faces.flatten()), GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        glDisable(GL_LIGHTING)

        glPopMatrix()

    def calculate_normals(self):
        normals = np.zeros_like(self.vertices)
        for face in self.faces:
            v0 = self.vertices[face[0]]
            v1 = self.vertices[face[1]]
            v2 = self.vertices[face[2]]
            normal = np.cross(v1 - v0, v2 - v0)
            normal /= np.linalg.norm(normal)
            for vertex_index in face:
                normals[vertex_index] += normal
        normals /= np.linalg.norm(normals, axis=1, keepdims=True)
        return normals.astype(np.float32)

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
            new_scale = max(min_scale, self.transform.scale[0] + factor)
            self.transform.scale[0] = new_scale
        elif axis == (0, 1, 0):
            new_scale = max(min_scale, self.transform.scale[1] + factor)
            self.transform.scale[1] = new_scale
        elif axis == (0, 0, 1):
            new_scale = max(min_scale, self.transform.scale[2] + factor)
            self.transform.scale[2] = new_scale

    def translate(self, distance, axis):
        if axis == (1, 0, 0):
            self.position[0] += distance
        elif axis == (0, 1, 0):
            self.position[1] += distance
        elif axis == (0, 0, 1):
            self.position[2] += distance

    def reset_transform(self):
        self.transform.reset()
        self.position = [0, 0, 0]

    def set_selected(self, selected):
        self.selected = selected
