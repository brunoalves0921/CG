from objects import Object
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image

class Cylinder(Object):
    def __init__(self, radius=1, height=2, slices=20, texture=None):
        super().__init__([0, 0, 0])
        self.selected = False
        self.radius = radius
        self.height = height
        self.slices = slices
        self.scale_factor = [1.0, 1.0, 1.0]

        self.vertices, self.side_faces, self.top_bottom_faces, self.uvs = self.generate_geometry()
        self.normals = self.calculate_normals()

        self.texture = texture
        self.texture_id = None
        self.texture_loaded = False

        self.vbo_vertices = glGenBuffers(1)
        self.vbo_side_faces = glGenBuffers(1)
        self.vbo_top_bottom_faces = glGenBuffers(1)
        self.vbo_normals = glGenBuffers(1)
        self.vbo_uvs = glGenBuffers(1)

        self.init_vbo()

        if self.texture:
            self.load_texture(self.texture)

    def generate_geometry(self):
        vertices = []
        side_faces = []
        top_bottom_faces = []
        uvs = []

        for j in [0, self.height]:
            for i in range(self.slices):
                angle = 2 * np.pi * i / self.slices
                x = self.radius * np.cos(angle)
                z = self.radius * np.sin(angle)
                y = j
                vertices.append((x, y, z))
                u = i / self.slices
                v = j / self.height
                uvs.append((u, v))

        bottom_center_index = len(vertices)
        vertices.append((0, 0, 0))
        uvs.append((0.5, 0.5))
        top_center_index = len(vertices)
        vertices.append((0, self.height, 0))
        uvs.append((0.5, 0.5))

        for i in range(self.slices):
            next_i = (i + 1) % self.slices
            bottom_current = i
            bottom_next = next_i
            top_current = i + self.slices
            top_next = next_i + self.slices
            side_faces.append((bottom_current, bottom_next, top_next, top_current))
            top_bottom_faces.append((bottom_center_index, i, next_i))
            top_bottom_faces.append((top_center_index, top_next, top_current))

        return np.array(vertices, dtype=np.float32), np.array(side_faces, dtype=np.uint32), np.array(top_bottom_faces, dtype=np.uint32), np.array(uvs, dtype=np.float32)

    def load_texture(self, file_path):
        if not self.texture_loaded:
            try:
                # Carregar a imagem
                image = Image.open(file_path)
                # Converter a imagem para RGB (no caso de imagens em outros formatos)
                image = image.convert("RGB")
                # Obter dados da imagem
                image_data = np.array(image, dtype=np.uint8)
                
                # Verificar se a textura já foi carregada
                if self.texture_id:
                    glDeleteTextures([self.texture_id])
                
                # Gerar e vincular a nova textura
                self.texture_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, self.texture_id)
                
                # Definir os parâmetros da textura
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                
                # Carregar a imagem para a textura
                glTexImage2D(
                    GL_TEXTURE_2D, 
                    0, 
                    GL_RGB, 
                    image.width, 
                    image.height, 
                    0, 
                    GL_RGB, 
                    GL_UNSIGNED_BYTE, 
                    image_data
                )
                
                # Marcar a textura como carregada
                self.texture_loaded = True
                self.texture = file_path
            except Exception as e:
                print(f"Erro ao carregar textura: {e}")

    def to_dict(self):
        return {
            'type': 'cylinder',
            'position': self.position,
            'rotation': self.transform.rotation,
            'scale': self.scale_factor,
            'radius': self.radius,
            'height': self.height,
            'slices': self.slices,
            'texture': self.texture
        }

    @classmethod
    def from_dict(cls, data):
        radius = data['radius']
        height = data['height']
        slices = data['slices']
        texture = data.get('texture')
        cylinder = cls(radius=radius, height=height, slices=slices, texture=texture)
        cylinder.position = data['position']
        cylinder.transform.rotation = data['rotation']
        cylinder.scale_factor = data['scale']
        return cylinder

    def init_vbo(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_side_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.side_faces.nbytes, self.side_faces, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_top_bottom_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.top_bottom_faces.nbytes, self.top_bottom_faces, GL_STATIC_DRAW)

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
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glNormalPointer(GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glTexCoordPointer(2, GL_FLOAT, 0, None)

        # Desenhar faces laterais
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_side_faces)
        glDrawElements(GL_QUADS, len(self.side_faces.flatten()), GL_UNSIGNED_INT, None)

        # Desenhar faces superior e inferior
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_top_bottom_faces)
        glDrawElements(GL_TRIANGLES, len(self.top_bottom_faces.flatten()), GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        glDisable(GL_LIGHTING)

        glPopMatrix()

    def calculate_normals(self):
        normals = np.zeros_like(self.vertices)

        # Calculate normals for side faces
        for face in self.side_faces:
            v0 = self.vertices[face[0]]
            v1 = self.vertices[face[1]]
            v2 = self.vertices[face[2]]
            v3 = self.vertices[face[3]]
            normal = np.cross(v1 - v0, v3 - v0)
            normal_length = np.linalg.norm(normal)
            if normal_length > 0:
                normal /= normal_length
            for vertex_index in face:
                normals[vertex_index] += normal
        
        # Normalize normals
        normals_length = np.linalg.norm(normals, axis=1, keepdims=True)
        valid_normals = np.squeeze(normals_length > 0)
        normals[valid_normals] /= normals_length[valid_normals]

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

    def shear(self, shear_factor, plane):
        pass
