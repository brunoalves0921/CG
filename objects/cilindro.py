from objects import Object
from OpenGL.GL import *
from PIL import Image
import numpy as np

class Cylinder(Object):
    def __init__(self, position=[0,0,0], rotation=None, scale=None, texture=None, radius=1.0, height=2.0, segments=32):
        super().__init__(position)
        self.transform.rotation = rotation if rotation is not None else [0, 0, 0]
        self.transform.scale = scale if scale is not None else [1, 1, 1]
        self.selected = False
        self.radius = radius
        self.height = height
        self.segments = segments
        self.vertices, self.faces, self.uvs = self.generate_geometry()
        self.normals = self.calculate_normals()
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

    def generate_geometry(self):
        vertices = []
        faces = []
        uvs = []

        # Lateral do cilindro
        for i in range(self.segments):
            angle = 2 * np.pi * i / self.segments
            x = self.radius * np.cos(angle)
            z = self.radius * np.sin(angle)
            vertices.append([x, 0, z])  # Ajustado para começar no y = 0
            vertices.append([x, self.height, z])  # Ajustado para o topo no y = self.height
            uvs.append([i / self.segments, 0])
            uvs.append([i / self.segments, 1])
            
            next_i = (i + 1) % self.segments
            faces.append([i * 2, next_i * 2, i * 2 + 1])
            faces.append([next_i * 2, next_i * 2 + 1, i * 2 + 1])

        # Tampa inferior
        bottom_center_index = len(vertices)
        vertices.append([0, 0, 0])  # Centro do fundo do cilindro
        uvs.append([0.5, 0.5])
        for i in range(self.segments):
            angle = 2 * np.pi * i / self.segments
            x = self.radius * np.cos(angle)
            z = self.radius * np.sin(angle)
            vertices.append([x, 0, z])
            uvs.append([0.5 + 0.5 * np.cos(angle), 0.5 + 0.5 * np.sin(angle)])
            next_i = (i + 1) % self.segments
            faces.append([bottom_center_index, bottom_center_index + i + 1, bottom_center_index + next_i + 1])

        # Tampa superior
        top_center_index = len(vertices)
        vertices.append([0, self.height, 0])  # Centro do topo do cilindro
        uvs.append([0.5, 0.5])
        for i in range(self.segments):
            angle = 2 * np.pi * i / self.segments
            x = self.radius * np.cos(angle)
            z = self.radius * np.sin(angle)
            vertices.append([x, self.height, z])
            uvs.append([0.5 + 0.5 * np.cos(angle), 0.5 + 0.5 * np.sin(angle)])
            next_i = (i + 1) % self.segments
            faces.append([top_center_index, top_center_index + next_i + 1, top_center_index + i + 1])

        vertices = np.array(vertices, dtype=np.float32)
        faces = np.array(faces, dtype=np.uint32)
        uvs = np.array(uvs, dtype=np.float32)

        return vertices, faces, uvs


    def calculate_normals(self):
        normals = np.zeros_like(self.vertices, dtype=np.float32)

        for face in self.faces:
            v1 = self.vertices[face[1]] - self.vertices[face[0]]
            v2 = self.vertices[face[2]] - self.vertices[face[0]]
            face_normal = np.cross(v1, v2)
            face_normal /= np.linalg.norm(face_normal)

            for vertex_index in face:
                normals[vertex_index] += face_normal

        # Invertendo todas as normais
        normals *= -1

        # invertendo as normais das faces superiores e inferiores
        for i in range(self.segments * 2, len(self.vertices)):
            normals[i] *= -1

        return normals
    
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
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glNormalPointer(GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glTexCoordPointer(2, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glDrawElements(GL_TRIANGLES, len(self.faces) * 3, GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        if self.texture_id:
            glDisable(GL_TEXTURE_2D)

        #Restaura a cor anterior
        glColor3f(*previous_color[:3])

        glPopMatrix()


    def to_dict(self):
        return {
            'type': 'cylinder',
            'position': self.position,
            'rotation': self.transform.rotation,
            'scale': self.transform.scale,
            'texture': self.texture,
            'radius': self.radius,
            'height': self.height,
            'segments': self.segments
        }

    @classmethod
    def from_dict(cls, data):
        position = data['position']
        rotation = data['rotation']
        scale = data['scale']
        texture = data.get('texture')
        radius = data.get('radius', 1.0)
        height = data.get('height', 2.0)
        segments = data.get('segments', 32)
        return cls(position=position, rotation=rotation, scale=scale, texture=texture, radius=radius, height=height, segments=segments)

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
