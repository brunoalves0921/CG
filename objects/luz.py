from objects import Object
from utils.transform import Transform
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class LightSphere(Object):
    def __init__(self, radius=0.3, intensity=10.0, color=(1.0, 1.0, 1.0), slices=16, stacks=16):
        super().__init__([0, 0, 0])
        self.radius = radius
        self.intensity = intensity
        self.color = color
        self.direction = [0, 0, -1]  # Direção da luz
        self.light_id = GL_LIGHT0

        self.slices = slices
        self.stacks = stacks

        self.selected = False  # Definição do atributo 'selected'

        self.vbo_vertices = glGenBuffers(1)
        self.vbo_indices = glGenBuffers(1)

        self.vertices, self.indices = self.create_sphere(radius, slices, stacks)
        self.init_vbo()

        # Configura a luz na criação do objeto
        self.update_light()

    def create_sphere(self, radius, slices, stacks):
        vertices = []
        indices = []

        # Gerar vértices e índices para a esfera
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_TRUE)

        # Desenhar a esfera em um buffer para obter os vértices e índices
        gluSphere(quadric, radius, slices, stacks)
        gluDeleteQuadric(quadric)

        # Placeholder para a criação de vértices e índices
        # Substitua isso com a geração real de vértices e índices
        # Adicione seus próprios cálculos de vértices e índices aqui

        return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

    def init_vbo(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_indices)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

    def update_light(self):
        # Atualiza a posição e a direção da luz usando a matriz de visualização da câmera
        glLightfv(self.light_id, GL_POSITION, [*self.position, 1.0])
        glLightfv(self.light_id, GL_DIFFUSE, [*self.color, self.intensity])
        glLightfv(self.light_id, GL_SPECULAR, [*self.color, self.intensity])
        glLightfv(self.light_id, GL_SPOT_DIRECTION, self.direction)
        glLightf(self.light_id, GL_SPOT_CUTOFF, 10.0)  # Definir o ângulo de corte do feixe em 10 graus
        glLightf(self.light_id, GL_SPOT_EXPONENT, 2.0)  # Controlar a intensidade da luz dentro do feixe

    def set_position(self, position):
        self.position = position
        self.update_light()

    def set_intensity(self, intensity):
        self.intensity = intensity
        self.update_light()

    def set_color(self, color):
        self.color = color
        self.update_light()

    def set_direction(self, direction):
        self.direction = direction
        self.update_light()

    def rotate(self, angle, axis):
        rotation_matrix = self.rotation_matrix(angle, axis)
        self.direction = np.dot(rotation_matrix, self.direction)
        self.update_light()

    def rotation_matrix(self, angle, axis):
        angle = np.radians(angle)
        x, y, z = axis
        c = np.cos(angle)
        s = np.sin(angle)
        t = 1 - c

        return np.array([
            [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
            [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
            [t * x * z - s * y, t * y * z + s * x, t * z * z + c]
        ])

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
        self.update_light()

    def reset_transform(self):
        self.transform.reset()
        self.position = [0, 0, 0]
        self.update_light()

    def set_selected(self, selected):
        self.selected = selected

    def update_light_transform(self):
        # Atualiza a luz para considerar a rotação da câmera
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.transform.rotation[0], 1, 0, 0)
        glRotatef(self.transform.rotation[1], 0, 1, 0)
        glRotatef(self.transform.rotation[2], 0, 0, 1)
        self.update_light()
        glPopMatrix()

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)

        # Configurar a cor do material
        if self.selected:
            glColor3f(1.0, 0.5, 0.0)  # Cor laranja se selecionado
        else:
            glColor3f(*self.color)  # Cor da luz

        # Desenhar a esfera usando a função GLU
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_FALSE)

        gluSphere(quadric, self.radius, self.slices, self.stacks)
        gluDeleteQuadric(quadric)

        glPopMatrix()

        # Atualiza a luz após desenhar o objeto
        self.update_light_transform()

        # Desenhar a seta para indicar a direção da luz
        self.draw_arrow()

    def draw_arrow(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glColor3f(1.0, 0.0, 0.0)  # Cor vermelha para a seta

        # Rotacionar a seta na direção da luz
        angle = np.arccos(np.dot([0, 0, -1], self.direction))
        axis = np.cross([0, 0, -1], self.direction)
        if np.linalg.norm(axis) > 0:
            glRotatef(np.degrees(angle), *axis)

        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -self.radius * 2)
        glEnd()

        glPopMatrix()

    def to_dict(self):
        return {
            'type': 'light_sphere',
            'position': self.position,
            'radius': self.radius,
            'intensity': self.intensity,
            'color': self.color,
            'direction': self.direction,
            'selected': self.selected  # Adicionar 'selected' ao dicionário
        }

    @classmethod
    def from_dict(cls, data):
        radius = data['radius']
        intensity = data['intensity']
        color = data['color']
        direction = data['direction']
        selected = data.get('selected', False)  # Adicionar 'selected' ao carregamento
        light_sphere = cls(radius=radius, intensity=intensity, color=color)
        light_sphere.position = data['position']
        light_sphere.direction = direction
        light_sphere.selected = selected  # Definir 'selected'
        return light_sphere

    def delete(self):
        glDisable(self.light_id)
        glDeleteBuffers(1, [self.vbo_vertices])
        glDeleteBuffers(1, [self.vbo_indices])

