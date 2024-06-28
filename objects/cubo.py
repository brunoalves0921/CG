from objects import Object
from objects import Object
from OpenGL.GL import *
from PIL import Image
import numpy as np
from utils.transform import Transform  # Certifique-se de importar corretamente a classe Transform

class Cube(Object):
    def __init__(self, position=None, rotation=None, scale=None, shear=None, texture=None):
        super().__init__([0, 0, 0])
        self.transform = Transform(position, rotation, scale)
        self.shear = shear  # Adicione o atributo shear
        self.selected = False
        self.vertices = self.generate_vertices()
        self.faces = self.generate_faces()
        self.uvs = self.generate_uvs()
        self.normals = self.calculate_normals()
        self.texture = texture
        self.texture_id = None
        self.texture_loaded = False

        # VBO IDs
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_faces = glGenBuffers(1)
        self.vbo_uvs = glGenBuffers(1)

        self.init_vbo()
        
        if self.texture:
            self.load_texture(self.texture)  # Carrega a textura se o caminho estiver disponível

    def generate_vertices(self):
        vertices = [
            # Front face
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1, 1, 1],
            # Back face
            [-1, -1, -1],
            [-1, 1, -1],
            [1, 1, -1],
            [1, -1, -1],
            # Left face
            [-1, -1, -1],
            [-1, -1, 1],
            [-1, 1, 1],
            [-1, 1, -1],
            # Right face
            [1, -1, -1],
            [1, 1, -1],
            [1, 1, 1],
            [1, -1, 1],
            # Top face
            [-1, 1, -1],
            [-1, 1, 1],
            [1, 1, 1],
            [1, 1, -1],
            # Bottom face
            [-1, -1, -1],
            [1, -1, -1],
            [1, -1, 1],
            [-1, -1, 1]
        ]
        return np.array(vertices, dtype=np.float32)

    def generate_faces(self):
        faces = [
            (0, 1, 2, 3),  # Front face
            (4, 5, 6, 7),  # Back face
            (8, 9, 10, 11),  # Left face
            (12, 13, 14, 15),  # Right face
            (16, 17, 18, 19),  # Top face
            (20, 21, 22, 23)  # Bottom face
        ]
        return np.array(faces, dtype=np.uint32)

    def generate_uvs(self):
        uvs = [
            # Front face
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            # Back face
            [1, 0],
            [1, 1],
            [0, 1],
            [0, 0],
            # Left face
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            # Right face
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            # Top face
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            # Bottom face
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ]
        return np.array(uvs, dtype=np.float32)

    def to_dict(self):
        return {
            'type': 'cube',
            'position': self.transform.position,
            'rotation': self.transform.rotation,
            'scale': self.transform.scale,
            'texture': self.texture,
        }

    @classmethod
    def from_dict(cls, data):
        position = data['position']
        rotation = data['rotation']
        scale = data['scale']
        texture = data.get('texture')  # Usar get para evitar KeyError caso a chave não exista
        return cls(position=position, rotation=rotation, scale=scale, texture=texture)

    def load_texture(self, file_path):
        image = Image.open(file_path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image_data = np.array(list(image.getdata()), np.uint8)

        # Remove a textura anterior se existir
        if self.texture_loaded:
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
        # Upload vertices to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Upload faces to VBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

        # Upload UVs to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glBufferData(GL_ARRAY_BUFFER, self.uvs.nbytes, self.uvs, GL_STATIC_DRAW)

    def calculate_normals(self):
        normals = np.zeros_like(self.vertices)

        # Faces frontais
        normals[0:4] = [0, 0, 1]
        # Faces traseiras
        normals[4:8] = [0, 0, -1]
        # Faces laterais esquerdas
        normals[8:12] = [-1, 0, 0]
        # Faces laterais direitas
        normals[12:16] = [1, 0, 0]
        # Faces superiores
        normals[16:20] = [0, 1, 0]
        # Faces inferiores
        normals[20:24] = [0, -1, 0]

        return normals.astype(np.float32)

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.transform.position)
        
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
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glTexCoordPointer(2, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        
        for face in range(6):
            glDrawElements(GL_QUADS, 4, GL_UNSIGNED_INT, ctypes.c_void_p(face * 4 * 4))

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
            self.transform.position[0] += distance
        elif axis == (0, 1, 0):
            self.transform.position[1] += distance
        elif axis == (0, 0, 1):
            self.transform.position[2] += distance

    def shear(self, shear_factor, plane):
        shear_matrix = np.identity(4)
        if plane == 'xy':
            shear_matrix[0][1] = shear_factor
        elif plane == 'xz':
            shear_matrix[0][2] = shear_factor
        elif plane == 'yx':
            shear_matrix[1][0] = shear_factor
        elif plane == 'yz':
            shear_matrix[1][2] = shear_factor
        elif plane == 'zx':
            shear_matrix[2][0] = shear_factor
        elif plane == 'zy':
            shear_matrix[2][1] = shear_factor

        for i in range(len(self.vertices)):
            vertex = np.append(self.vertices[i], 1)
            transformed_vertex = np.dot(shear_matrix, vertex)
            self.vertices[i] = transformed_vertex[:3]

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
