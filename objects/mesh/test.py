from objects import Object
from OBJFileLoader import OBJ
from PIL import Image, UnidentifiedImageError
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.GLUT import *
from utils.transform import Transform
import os

class Mesh(Object):
    def __init__(self, position, filename, rotation=None, scale=None, texture=None, swapyz=False, default_mtl=('objects/mesh/default.mtl', 'Material')):
        super().__init__(position)
        self.transform = Transform(position, rotation, scale)
        self.texture = texture
        self.texture_id = None
        self.texture_loaded = False
        self.filename = filename
        self.selected = False
        self.vbo = None
        self.ibo = None

        if not filename:
            raise ValueError("filename deve ser fornecido para carregar o objeto .obj")

        self.model = OBJ(filename, swapyz, default_mtl=default_mtl)
        if self.texture and self.is_image_file(self.texture):
            self.load_texture(self.texture)
        else:
            self.load_texture(default_mtl[0])

        self.create_vbo()

    def create_vbo(self):
        vertices = self.model.vertices
        normals = self.model.normals
        texcoords = self.model.texcoords
        faces = self.model.faces

        if vertices:
            flattened_vertices = [coord for vertex in vertices for coord in vertex]
            flattened_normals = [coord for normal in normals for coord in normal]
            flattened_texcoords = [coord for texcoord in texcoords for coord in texcoord]

            # Extract indices and flatten them
            indices = []
            for face in faces:
                for vertex in face[0]:  # face[0] contém os índices dos vértices
                    indices.append(vertex - 1)  # -1 para ajustar ao índice base 0 do OpenGL

            self.vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

            vertex_data = flattened_vertices + flattened_normals + flattened_texcoords
            array_type = (GLfloat * len(vertex_data))
            glBufferData(GL_ARRAY_BUFFER, len(vertex_data) * 4, array_type(*vertex_data), GL_STATIC_DRAW)

            self.ibo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

            index_array_type = (GLuint * len(indices))
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, index_array_type(*indices), GL_STATIC_DRAW)

            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def is_image_file(self, file_path):
        return file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'))

    def load_texture(self, file_path):
        if not self.is_image_file(file_path):
            print(f"Arquivo '{file_path}' não é uma imagem. Ignorando a textura.")
            return

        try:
            # Abre a imagem e converte para RGB se necessário
            image = Image.open(file_path)
            image = image.convert("RGB")
            image_data = np.array(image, dtype=np.uint8)
            
            # Transpor a imagem para o formato adequado (OpenGL requer que as imagens sejam lidas de baixo para cima)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image_data = np.array(image, dtype=np.uint8)

            # Verifica o número de canais da imagem para definir o formato correto
            if image.mode == 'RGBA':
                mode = GL_RGBA
            else:
                mode = GL_RGB

            # Remove a textura anterior se existir
            if self.texture_id:
                glDeleteTextures([self.texture_id])

            # Gera e configura a nova textura
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, mode, image.width, image.height, 0, mode, GL_UNSIGNED_BYTE, image_data)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

            # Marca a textura como carregada
            self.texture_loaded = True
            self.texture = file_path

        except FileNotFoundError:
            print(f"Textura não encontrada: {file_path}")
        except UnidentifiedImageError:
            print(f"Arquivo '{file_path}' não é uma imagem válida.")
        except Exception as e:
            print(f"Erro ao carregar textura: {e}")

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.transform.position)

        # Verifica se rotation é uma lista antes de aplicar rotação
        if isinstance(self.transform.rotation, list) and len(self.transform.rotation) == 3:
            glRotatef(self.transform.rotation[0], 1, 0, 0)
            glRotatef(self.transform.rotation[1], 0, 1, 0)
            glRotatef(self.transform.rotation[2], 0, 0, 1)
        else:
            print("A rotação deve ser uma lista de três valores.")

        glScalef(*self.transform.scale)

        if self.selected:
            glColor3f(1.0, 0.5, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)

        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

        if self.vbo and self.ibo:
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)

            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            stride = 3 * 4  # number of floats per vertex/normal/texcoord
            offset = len(self.model.vertices) * stride

            glVertexPointer(3, GL_FLOAT, stride, ctypes.c_void_p(0))
            glNormalPointer(GL_FLOAT, stride, ctypes.c_void_p(offset))
            glTexCoordPointer(2, GL_FLOAT, stride, ctypes.c_void_p(3 * len(self.model.vertices) * 4))

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
            glDrawElements(GL_TRIANGLES, len(self.model.faces) * 3, GL_UNSIGNED_INT, None)

            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        else:
            self.model.render()

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        glPopMatrix()

    def rotate_mesh(self, angle, axis):
        if axis == (1, 0, 0):
            self.transform.rotation[0] += angle
        elif axis == (0, 1, 0):
            self.transform.rotation[1] += angle
        elif axis == (0, 0, 1):
            self.transform.rotation[2] += angle

    def scale_mesh(self, factor, axis):
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

    def translate_mesh(self, distance, axis):
        if axis == (1, 0, 0):
            self.transform.position[0] += distance
        elif axis == (0, 1, 0):
            self.transform.position[1] += distance
        elif axis == (0, 0, 1):
            self.transform.position[2] += distance

    def to_dict(self):
        return {
            'type': 'mesh',
            'position': self.transform.position,
            'rotation': self.transform.rotation,
            'scale': self.transform.scale,
            'texture': self.texture,
            'filename': self.filename,
        }

    @classmethod
    def from_dict(cls, data):
        position = data['position']
        rotation = data['rotation']
        scale = data['scale']
        texture = data.get('texture')
        filename = data['filename']
        return cls(position=position, filename=filename, rotation=rotation, scale=scale, texture=texture)
