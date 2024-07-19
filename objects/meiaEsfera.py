from objects import Object
from OpenGL.GL import *
from PIL import Image
import numpy as np

class HalfSphere(Object):
    def __init__(self, position=None, rotation=None, scale=None, texture=None):
        super().__init__(position)
        self.transform.rotation = rotation if rotation is not None else [0, 0, 0]
        self.transform.scale = scale if scale is not None else [1, 1, 1]
        self.selected = False
        self.vertices, self.normals, self.uvs = self.generate_hemisphere(32, 32)
        self.faces = self.generate_faces(32, 32)
        self.texture = texture
        self.texture_id = None
        self.texture_loaded = False

        # VBO IDs
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_faces = glGenBuffers(1)
        self.vbo_uvs = glGenBuffers(1)
        self.vbo_normals = glGenBuffers(1)

        self.init_vbo()

        if self.texture:
            self.load_texture(self.texture)

    def generate_hemisphere(self, slices, stacks):
        vertices = []
        normals = []
        uvs = []

        for i in range(stacks + 1):
            theta = i * np.pi / stacks
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)

            for j in range(slices + 1):
                phi = j * 2 * np.pi / slices
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)

                x = cos_phi * sin_theta
                y = cos_theta
                z = sin_phi * sin_theta
                u = 1 - (j / slices)
                v = 1 - (i / stacks)

                # Ensure we are only generating vertices for the upper half of the sphere
                if y >= 0:
                    vertices.append([x, y, z])
                    normals.append([x, y, z])
                    uvs.append([u, v])

        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        uvs = np.array(uvs, dtype=np.float32)

        return vertices, normals, uvs

    def generate_faces(self, slices, stacks):
        faces = []

        for i in range(stacks):
            for j in range(slices):
                v1 = i * (slices + 1) + j
                v2 = v1 + slices + 1
                # Only add faces for vertices in the upper half of the hemisphere
                if v2 < len(self.vertices) and v1 < len(self.vertices):
                    faces.append((v1, v2, v2 + 1, v1 + 1))

        return np.array(faces, dtype=np.uint32)

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

        # Upload normals to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)

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
            glColor3f(1.0, 1.0, 1.0)

        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

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
        glDrawElements(GL_QUADS, self.faces.size, GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        glPopMatrix()

    def to_dict(self):
        return {
            'type': 'hemisphere',
            'position': self.position,
            'rotation': self.transform.rotation,
            'scale': self.transform.scale,
            'texture': self.texture,
        }

    @classmethod
    def from_dict(cls, data):
        position = data['position']
        rotation = data['rotation']
        scale = data['scale']
        texture = data.get('texture')
        return cls(position=position, rotation=rotation, scale=scale, texture=texture)

    def load_texture(self, file_path):
        try:
            image = Image.open(file_path)
            image = image.convert("RGB")
            image_data = np.array(image, dtype=np.uint8)

            if image.mode == 'RGBA':
                mode = GL_RGBA
            else:
                mode = GL_RGB

            if self.texture_id:
                glDeleteTextures([self.texture_id])

            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, mode, image.width, image.height, 0, mode, GL_UNSIGNED_BYTE, image_data)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

            self.texture_loaded = True
            self.texture = file_path
        except FileNotFoundError:
            print(f"Textura não encontrada: {file_path}")
        except Exception as e:
            print(f"Erro ao carregar textura: {e}")

    def rotate(self, angle, axis):
        if axis == (1, 0, 0):
            self.transform.rotation[0] += angle
        elif axis == (0, 1, 0):
            self.transform.rotation[1] += angle
        elif axis == (0, 0, 1):
            self.transform.rotation[2] += angle

    def scale(self, factor, axis):
        min_scale = 0.05
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
