from objects import Object
from OpenGL.GL import *
import numpy as np

class Cube(Object):
    base_vertices = np.array([
        [1, -1, -1],  # 0
        [1, 1, -1],
        [-1, 1, -1],
        [-1, -1, -1],  # 3
        [1, -1, 1],
        [1, 1, 1],
        [-1, -1, 1],
        [-1, 1, 1]  # 7
    ], dtype=np.float32)

    edges = np.array([
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [5, 7],
        [7, 6],
        [6, 4],
        [0, 4],
        [1, 5],
        [2, 7],
        [3, 6]
    ], dtype=np.uint32)

    faces = np.array([
        [0, 1, 2, 3],
        [3, 2, 7, 6],
        [6, 7, 5, 4],
        [4, 5, 1, 0],
        [1, 5, 7, 2],
        [4, 0, 3, 6]
    ], dtype=np.uint32)

    def __init__(self):
        super().__init__([0, 0, 0])
        self.selected = False
        self.vertices = Cube.base_vertices.copy()
        self.scale_factor = [1.0, 1.0, 1.0]  # Adicionar atributo para controle da escala

        # VBO IDs
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_edges = glGenBuffers(1)
        self.vbo_faces = glGenBuffers(1)

        self.init_vbo()

    def init_vbo(self):
        # Upload vertices to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Upload edges to VBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_edges)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.edges.nbytes, self.edges, GL_STATIC_DRAW)

        # Upload faces to VBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        
        glRotatef(self.transform.rotation[0], 1, 0, 0)
        glRotatef(self.transform.rotation[1], 0, 1, 0)
        glRotatef(self.transform.rotation[2], 0, 0, 1)

        glScalef(*self.scale_factor)  # Aplicar escala
        
        # Definir cor do cubo se selecionado ou não
        if self.selected:
            glColor3f(1.0, 0.5, 0.0)
        else:
            glColor3f(0.5, 0.5, 0.5)
        
        # Desenhar faces do cubo
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glDrawElements(GL_QUADS, len(Cube.faces) * 4, GL_UNSIGNED_INT, None)
        
        glDisableClientState(GL_VERTEX_ARRAY)

        # Desenhar arestas do cubo
        glColor3f(0, 0, 0)
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_edges)
        glDrawElements(GL_LINES, len(Cube.edges) * 2, GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)

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
        shear_matrix = np.identity(4)
        if plane == 'xy':
            shear_matrix[0][1] = shear_factor  # Shear X based on Y
            
        new_vertices = []
        for vertex in self.vertices:
            v = np.array(vertex.tolist() + [1])  # Adiciona 1 para transformação homogênea
            if (plane in ['xy', 'xz'] and vertex[1] >= 0) or \
               (plane in ['yx', 'yz'] and vertex[0] >= 0) or \
               (plane in ['zx', 'zy'] and vertex[2] >= 0):
                v_new = shear_matrix @ v
                new_vertices.append(v_new[:3].tolist())
            else:
                new_vertices.append(vertex.tolist())
        
        self.vertices = np.array(new_vertices, dtype=np.float32)
        self.init_vbo()  # Re-upload vertices to VBO
