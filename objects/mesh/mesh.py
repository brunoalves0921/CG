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

        if not filename:
            raise ValueError("filename deve ser fornecido para carregar o objeto .obj")
        
        self.model = OBJ(filename, swapyz, default_mtl=default_mtl)
        
        # if self.texture and self.is_image_file(self.texture):
        #     self.load_texture(self.texture)
        # else:
        #     self.load_texture(default_mtl[0])

    def is_image_file(self, file_path):
        return file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'))

    def load_texture(self, file_path):
    #     if not self.is_image_file(file_path):
    #         print(f"Arquivo '{file_path}' não é uma imagem. Ignorando a textura.")
    #         return

        try:
            image = Image.open(file_path)
            image = image.convert("RGBA")  # Garantir que a imagem tem um canal alpha
            image_data = np.array(image, dtype=np.uint8)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image_data = np.array(image, dtype=np.uint8)

            mode = GL_RGBA

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
        except UnidentifiedImageError:
            print(f"Arquivo '{file_path}' não é uma imagem válida.")
        except Exception as e:
            print(f"Erro ao carregar textura: {e}")

    def draw(self, is_shadow=False):
        glPushMatrix()
        glTranslatef(*self.transform.position)
        
        if isinstance(self.transform.rotation, list) and len(self.transform.rotation) == 3:
            glRotatef(self.transform.rotation[0], 1, 0, 0)
            glRotatef(self.transform.rotation[1], 0, 1, 0)
            glRotatef(self.transform.rotation[2], 0, 0, 1)
        else:
            print("A rotação deve ser uma lista de três valores.")

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
        else:
            glDisable(GL_TEXTURE_2D)

        # Habilita o blending antes de renderizar
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.model.render()

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        # Desabilita o blending após renderizar
        glDisable(GL_BLEND)

        # Restaura a cor anterior
        glColor3f(*previous_color[:3])

        glPopMatrix()

    def rotate_mesh(self, angle, axis):
        if axis == (1, 0, 0):
            self.transform.rotation[0] += angle
        elif axis == (0, 1, 0):
            self.transform.rotation[1] += angle
        elif axis == (0, 0, 1):
            self.transform.rotation[2] += angle

    def scale_mesh(self, factor, axis):
        min_scale = 0.01
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
