from objects import Object
from OpenGL.GL import *
import numpy as np
from PIL import Image

class Cone(Object):
    def __init__(self, base_radius=1, height=2, slices=20, texture=None):
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
        self.vbo_normals = glGenBuffers(1)
        self.vbo_tex_coords = glGenBuffers(1)  # VBO para coordenadas de textura

        self.init_vbo()

        self.texture = texture  # Atributo para armazenar o caminho da textura
        self.texture_id = None
        self.texture_loaded = False  # Flag para controlar se a textura já foi carregada

        if self.texture:
            self.load_texture(self.texture)

    def generate_vertices(self):
        vertices = [(0, 0, 0)]  # Centro da base
        angle_increment = 2 * np.pi / self.slices
        for i in range(self.slices):
            angle = i * angle_increment
            x = self.base_radius * np.cos(angle)
            z = self.base_radius * np.sin(angle)
            vertices.append((x, 0, z))
        vertices.append((0, self.height, 0))  # Ápice do cone
        return np.array(vertices, dtype=np.float32)

    def generate_faces(self):
        faces = []
        for i in range(1, self.slices):
            faces.append((0, i, i+1))
        faces.append((0, self.slices, 1))  # Última face conectando ao primeiro vértice

        apex_index = len(self.vertices) - 1
        for i in range(1, self.slices):
            faces.append((apex_index, i, i+1))
        faces.append((apex_index, self.slices, 1))  # Última face lateral
        return np.array(faces, dtype=np.uint32)

    def init_vbo(self):
        # Carrega vértices no VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Carrega faces no VBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

        # Calcula normais
        self.normals = self.calculate_normals()

        # Carrega normais no VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)

        # Gera coordenadas de textura
        self.tex_coords = self.generate_texture_coords()

        # Carrega coordenadas de textura no VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_tex_coords)
        glBufferData(GL_ARRAY_BUFFER, self.tex_coords.nbytes, self.tex_coords, GL_STATIC_DRAW)

    def draw(self, is_shadow=False):
        glPushMatrix()
        glTranslatef(*self.position)
        
        glRotatef(self.transform.rotation[0], 1, 0, 0)
        glRotatef(self.transform.rotation[1], 0, 1, 0)
        glRotatef(self.transform.rotation[2], 0, 0, 1)

        glScalef(*self.scale_factor)
        
        previous_color = glGetFloatv(GL_CURRENT_COLOR)
        if not is_shadow:
            # Define a cor branca somente se não for sombra
            glColor3f(1.0, 1.0, 1.0)
        else:
            # Para a sombra, você pode definir uma cor específica ou uma cor de sombra
            glColor3f(0.0, 0.0, 0.0)  # Cor preta para a sombra
        
        if not is_shadow and self.selected:
            glColor3f(1.0, 0.5, 0.0)  # Aplica a cor laranja somente se selecionado e não for sombra
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glNormalPointer(GL_FLOAT, 0, None)

        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo_tex_coords)
            glTexCoordPointer(2, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glDrawElements(GL_TRIANGLES, len(self.faces.flatten()), GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        #Restaura a cor anterior
        glColor3f(*previous_color[:3])

        glPopMatrix()

    def calculate_normals(self):
        normals = np.zeros_like(self.vertices)
        for face in self.faces:
            v0 = self.vertices[face[0]]
            v1 = self.vertices[face[1]]
            v2 = self.vertices[face[2]]
            normal = np.cross(v1 - v0, v2 - v0)
            normal /= np.linalg.norm(normal)  # Normalize the normal vector
            for vertex_index in face:
                normals[vertex_index] += normal
        normals /= np.linalg.norm(normals, axis=1, keepdims=True)  # Normalize each normal individually
        
        # Invert the normals
        normals *= -1
        
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

    def generate_texture_coords(self):
        tex_coords = []
        for i in range(self.slices + 1):
            tex_coords.append([i / self.slices, 0])
        tex_coords.append([0.5, 1])  # Textura do vértice do ápice
        return np.array(tex_coords, dtype=np.float32)

    def to_dict(self):
        return {
            'type': 'cone',
            'position': self.position,
            'rotation': self.transform.rotation,
            'scale': self.scale_factor,
            'base_radius': self.base_radius,
            'height': self.height,
            'slices': self.slices,
            'texture': self.texture
        }

    @classmethod
    def from_dict(cls, data):
        base_radius = data['base_radius']
        height = data['height']
        slices = data['slices']
        texture = data.get('texture')
        cone = cls(base_radius=base_radius, height=height, slices=slices, texture=texture)
        cone.position = data['position']
        cone.transform.rotation = data['rotation']
        cone.scale_factor = data['scale']

        # Recalculate normals
        cone.vertices = cone.generate_vertices()
        cone.faces = cone.generate_faces()
        cone.normals = cone.calculate_normals()
        cone.init_vbo()

        if texture:
            cone.load_texture(texture)

        return cone
