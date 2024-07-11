import json
from objects import Object
from utils.transform import Transform
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class LightSphere(Object):
    def __init__(self, radius=0.2, intensity=10.0, color=(1.0, 1.0, 1.0), slices=16, stacks=16):
        super().__init__([0, 0, 0])
        self.radius = radius
        self.intensity = intensity
        self.color = color
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

        return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

    def init_vbo(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_indices)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

    def update_light(self):
        # Atualiza a posição e a intensidade da luz
        glLightfv(self.light_id, GL_POSITION, [*self.position, 1.0])
        glLightfv(self.light_id, GL_DIFFUSE, [*self.color, self.intensity])
        glLightfv(self.light_id, GL_SPECULAR, [*self.color, self.intensity])
        glLightf(self.light_id, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(self.light_id, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(self.light_id, GL_QUADRATIC_ATTENUATION, 0.0)

    def set_position(self, position):
        self.position = position
        self.update_light()

    def set_intensity(self, intensity):
        self.intensity = intensity
        self.update_light()

    def set_color(self, color):
        self.color = color
        self.update_light()

    def translate(self, distance, axis):
        if axis == (1, 0, 0):
            self.position[0] += distance
        elif axis == (0, 1, 0):
            self.position[1] += distance
        elif axis == (0, 0, 1):
            self.position[2] += distance
        self.update_light()

    def set_selected(self, selected):
        self.selected = selected

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
        self.update_light()


    def to_dict(self):
        return {
            'type': 'light_sphere',
            'position': self.position,
            'radius': self.radius,
            'intensity': self.intensity,
            'color': self.color,
            'selected': self.selected  # Adicionar 'selected' ao dicionário
        }

    @classmethod
    def from_dict(cls, data):
        radius = data['radius']
        intensity = data['intensity']
        color = data['color']
        selected = data.get('selected', False)  # Adicionar 'selected' ao carregamento
        light_sphere = cls(radius=radius, intensity=intensity, color=color)
        light_sphere.position = data['position']
        light_sphere.selected = selected  # Definir 'selected'
        return light_sphere

    def delete(self):
        print(f"Deleting light: {self.light_id}")  # Debug print

        # Resetar a posição e a intensidade da luz para garantir que ela não afete mais a cena
        zero_position = [0.0, 0.0, 0.0, 1.0]
        zero_color = [0.0, 0.0, 0.0, 0.0]
        
        glLightfv(self.light_id, GL_POSITION, zero_position)
        glLightfv(self.light_id, GL_DIFFUSE, zero_color)
        glLightfv(self.light_id, GL_SPECULAR, zero_color)
        glLightfv(self.light_id, GL_AMBIENT, zero_color)

        # Garantir que a atenuação esteja zerada
        glLightf(self.light_id, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(self.light_id, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(self.light_id, GL_QUADRATIC_ATTENUATION, 0.0)

        # Deletar buffers VBO associados ao objeto
        glDeleteBuffers(1, [self.vbo_vertices])
        glDeleteBuffers(1, [self.vbo_indices])


