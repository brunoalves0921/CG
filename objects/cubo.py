from objects import Object
from OpenGL.GL import *
from PIL import Image
import numpy as np

class Cube(Object):
    def __init__(self, position=None, rotation=None, scale=None, texture=None):
        super().__init__(position)
        self.transform.rotation = rotation if rotation is not None else [0, 0, 0]
        self.transform.scale = scale if scale is not None else [1, 1, 1]
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
        self.vbo_normals = glGenBuffers(1)  # Inicialização do VBO para as normais

        self.init_vbo()
        
        if self.texture:
            self.load_texture(self.texture)  # Carrega a textura se o caminho estiver disponível

    def get_center(self):
        return self.position

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

    def calculate_normals(self):
        normals = np.zeros_like(self.vertices, dtype=np.float32)

        for face in self.faces:
            v1 = self.vertices[face[1]] - self.vertices[face[0]]
            v2 = self.vertices[face[2]] - self.vertices[face[0]]
            face_normal = np.cross(v1, v2)
            face_normal /= np.linalg.norm(face_normal)

            for vertex_index in face:
                normals[vertex_index] += face_normal

        normals /= np.linalg.norm(normals, axis=1).reshape(-1, 1)

        return normals

    def draw(self, is_shadow=False):
        glPushMatrix()
        glTranslatef(*self.position)
        
        glRotatef(self.transform.rotation[0], 1, 0, 0)
        glRotatef(self.transform.rotation[1], 0, 1, 0)
        glRotatef(self.transform.rotation[2], 0, 0, 1)

        glScalef(*self.transform.scale)
        
        previous_color = glGetFloatv(GL_CURRENT_COLOR)
        if not is_shadow:
            # Define a cor branca somente se não for sombra
            glColor3f(1.0, 1.0, 1.0)
        else:
            # Para a sombra, você pode definir uma cor específica ou uma cor de sombra
            glColor3f(0.0, 0.0, 0.0)  # Cor preta para a sombra
        
        if not is_shadow and self.selected:
            glColor3f(1.0, 0.5, 0.0)  # Aplica a cor laranja somente se selecionado e não for sombra
            
        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)  # Habilita o uso de normais
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)  # Usa o VBO de normais
        glNormalPointer(GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glTexCoordPointer(2, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        
        for face in range(6):
            glDrawElements(GL_QUADS, 4, GL_UNSIGNED_INT, ctypes.c_void_p(face * 4 * 4))

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        # Restaura a cor anterior
        glColor3f(*previous_color[:3])

        glPopMatrix()

    def to_dict(self):
        return {
            'type': 'cube',
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
        texture = data.get('texture')  # Usar get para evitar KeyError caso a chave não exista
        return cls(position=position, rotation=rotation, scale=scale, texture=texture)

    def load_texture(self, file_path):
        try:
            image = Image.open(file_path)
            image = image.convert("RGBA")  # Garantir que a imagem tenha um canal alpha
            image_data = np.array(image, dtype=np.uint8)

            mode = GL_RGBA  # Usar GL_RGBA para texturas com canal alpha

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

            # Configura o blending para suportar transparência
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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
