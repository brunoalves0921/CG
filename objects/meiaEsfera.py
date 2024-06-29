from objects import Object
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image

class HalfSphere(Object):
    def __init__(self, radius=1, stacks=20, slices=20):
        super().__init__([0, 0, 0])
        self.selected = False
        self.radius = radius
        self.stacks = stacks
        self.slices = slices
        self.scale_factor = [1.0, 1.0, 1.0]

        self.vertices, self.faces, self.normals, self.uvs = self.generate_geometry()

        self.texture = None
        self.texture_id = None
        self.texture_loaded = False

        # VBO IDs
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_faces = glGenBuffers(1)
        self.vbo_normals = glGenBuffers(1)
        self.vbo_uvs = glGenBuffers(1)  # New VBO for UV coordinates

        self.init_vbo()

    def generate_geometry(self):
        vertices = []
        faces = []
        normals = []
        uvs = []

        for i in range(self.stacks + 1):
            theta = (i / self.stacks) * (np.pi / 2)
            for j in range(self.slices + 1):
                phi = (j / self.slices) * (2 * np.pi)
                x = self.radius * np.sin(theta) * np.cos(phi)
                z = self.radius * np.sin(theta) * np.sin(phi)
                y = self.radius * np.cos(theta)
                vertices.append((x, y, z))
                normal = np.array([x, y, z], dtype=np.float32)
                normals.append(normal / np.linalg.norm(normal))
                u = j / self.slices
                v = i / self.stacks
                uvs.append((u, v))

        for i in range(self.stacks):
            for j in range(self.slices):
                first = i * (self.slices + 1) + j
                second = first + self.slices + 1
                faces.append((first, second, first + 1))
                faces.append((second, second + 1, first + 1))

        return (
            np.array(vertices, dtype=np.float32),
            np.array(faces, dtype=np.uint32),
            np.array(normals, dtype=np.float32),
            np.array(uvs, dtype=np.float32)
        )

    def load_texture(self, file_path):
        if not self.texture_loaded:
            try:
                image = Image.open(file_path)
            except FileNotFoundError:
                print(f"Textura não encontrada: {file_path}")
                return
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image_data = np.array(list(image.getdata()), np.uint8)

            if self.texture_id:
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

        # Upload normals to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)

        # Upload UVs to VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_uvs)
        glBufferData(GL_ARRAY_BUFFER, self.uvs.nbytes, self.uvs, GL_STATIC_DRAW)

    def to_dict(self):
        data = {
            'type': 'halfsphere',
            'position': self.position,
            'rotation': self.transform.rotation,
            'scale': self.scale_factor,
            'radius': self.radius,
            'stacks': self.stacks,
            'slices': self.slices
        }
        if self.texture:
            data['texture'] = self.texture
        return data

    @classmethod
    def from_dict(cls, data):
        radius = data['radius']
        stacks = data['stacks']
        slices = data['slices']
        texture = data.get('texture')
        half_sphere = cls(radius=radius, stacks=stacks, slices=slices)
        half_sphere.position = data['position']
        half_sphere.transform.rotation = data['rotation']
        half_sphere.scale_factor = data['scale']
        if texture:
            half_sphere.load_texture(texture)
        return half_sphere

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

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_faces)
        glDrawElements(GL_TRIANGLES, len(self.faces) * 3, GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
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

    def reset_transform(self):
        self.transform.reset()
        self.position = [0, 0, 0]

    def set_selected(self, selected):
        self.selected = selected
