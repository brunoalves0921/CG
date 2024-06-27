from objects import Object
from OpenGL.GL import *
import numpy as np
from PIL import Image

class Pyramid(Object):
    def __init__(self, base_length=2, height=2):
        super().__init__([0, 0, 0])
        self.selected = False
        self.base_length = base_length
        self.height = height
        self.scale_factor = [1.0, 1.0, 1.0]

        self.vertices = np.array(self.generate_vertices(), dtype=np.float32)
        self.faces = np.array(self.generate_faces(), dtype=np.uint32)
        self.uvs = np.array(self.generate_uvs(), dtype=np.float32)

        self.texture = None
        self.texture_id = None
        self.texture_loaded = False

        # VBO IDs
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_faces = glGenBuffers(1)
        self.vbo_uvs = glGenBuffers(1)

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

    def generate_uvs(self):
        uvs = [
            (0, 0),  # UV coordinates for the base vertices
            (1, 0),
            (1, 1),
            (0, 1),
            (0.5, 0.5)  # UV coordinates for the apex
        ]
        return uvs

    def init_vbo(self):
        # Upload vertices to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Upload faces to VBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

        # Upload UVs to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glBufferData(GL_ARRAY_BUFFER, self.uvs.nbytes, self.uvs, GL_STATIC_DRAW)

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
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glTexCoordPointer(2, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        
        # Desenhar faces laterais (triângulos)
        for i in range(4):
            glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, ctypes.c_void_p(i * 3 * 4))
        
        # Desenhar faces da base (dois triângulos)
        for i in range(4, 6):
            glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, ctypes.c_void_p(i * 3 * 4))

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        glDisable(GL_LIGHTING)

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
