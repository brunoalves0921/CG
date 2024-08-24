import os
import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.arrays import vbo

class OBJ:
    generate_on_init = True
    
    @classmethod
    def loadTexture(cls, imagefile):
        surf = pygame.image.load(imagefile)
        image = pygame.image.tostring(surf, 'RGBA', 1)
        ix, iy = surf.get_rect().size
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glGenerateMipmap(GL_TEXTURE_2D)  # Generate mipmaps
        return texid

    @classmethod
    def loadMaterial(cls, filename):
        contents = {}
        mtl = None
        dirname = os.path.dirname(filename)

        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'newmtl':
                mtl = contents[values[1]] = {}
            elif mtl is None:
                raise ValueError("mtl file doesn't start with newmtl stmt")
            elif values[0] == 'map_Kd':
                # Load the texture referred to by this declaration
                mtl[values[0]] = values[1]
                imagefile = os.path.join(dirname, mtl['map_Kd'])
                mtl['texture_Kd'] = cls.loadTexture(imagefile)
            else:
                mtl[values[0]] = list(map(float, values[1:]))
        return contents

    def __init__(self, filename, swapyz=False, default_mtl: tuple[str, str]=None):
        """Loads a Wavefront OBJ file."""
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.vbo_vertices = None
        self.vbo_texcoords = None
        self.vbo_normals = None
        self.gl_list = 0
        dirname = os.path.dirname(filename)

        material = None
        if default_mtl is not None:
            path, mtl = default_mtl
            self.mtl = self.loadMaterial(path)
            material = mtl

        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = self.loadMaterial(os.path.join(dirname, values[1]))
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))

        if self.generate_on_init:
            self.generate()

    def generate(self):
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)

        # Data buffers
        data_vertices = []
        data_normals = []
        data_texcoords = []

        for face in self.faces:
            vertices, normals, texture_coords, material = face

            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                # Use diffuse texmap
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                # Just use diffuse color
                glColor(*mtl['Kd'])

            for i in range(len(vertices)):
                data_vertices.append(self.vertices[vertices[i] - 1])

                if normals[i] > 0:
                    data_normals.append(self.normals[normals[i] - 1])
                else:
                    data_normals.append((0, 0, 0))  # Default normal

                if texture_coords[i] > 0:
                    data_texcoords.append(self.texcoords[texture_coords[i] - 1])
                else:
                    data_texcoords.append((0, 0))  # Default texcoord

        # Convert lists to numpy arrays for VBO
        data_vertices = np.array(data_vertices, dtype='f')
        data_normals = np.array(data_normals, dtype='f')
        data_texcoords = np.array(data_texcoords, dtype='f')

        # Create VBOs
        self.vbo_vertices = vbo.VBO(data_vertices)
        self.vbo_normals = vbo.VBO(data_normals)
        self.vbo_texcoords = vbo.VBO(data_texcoords)

        # Bind and draw VBOs
        self.vbo_vertices.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vbo_vertices)

        self.vbo_normals.bind()
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, self.vbo_normals)

        self.vbo_texcoords.bind()
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, self.vbo_texcoords)

        # Use GL_POLYGON for each face
        face_start = 0
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            face_len = len(vertices)
            glDrawArrays(GL_POLYGON, face_start, face_len)
            face_start += face_len

        # Disable client states
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        # Unbind VBOs
        self.vbo_vertices.unbind()
        self.vbo_normals.unbind()
        self.vbo_texcoords.unbind()

        glDisable(GL_TEXTURE_2D)
        glEndList()

    def render(self):
        glCallList(self.gl_list)

    def __del__(self):
        if self.vbo_vertices:
            self.vbo_vertices.delete()
        if self.vbo_normals:
            self.vbo_normals.delete()
        if self.vbo_texcoords:
            self.vbo_texcoords.delete()
        if self.gl_list:
            try:
                glDeleteLists(self.gl_list, 1)
            except OpenGL.error.GLError:
                pass
