import json
from objects import Object
from utils.transform import Transform
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class LightSphere(Object):
    available_light_ids = [GL_LIGHT0 + i for i in range(7)]

    def __init__(self, radius=0.2, intensity=10.0, color=(1.0, 1.0, 1.0), slices=16, stacks=16):
        super().__init__([0, 0, 0])
        self.radius = radius
        self.intensity = intensity
        self.color = color

        self.slices = slices
        self.stacks = stacks

        self.selected = False  # Definição do atributo 'selected'

        self.vbo_vertices = glGenBuffers(1)
        self.vbo_indices = glGenBuffers(1)
        self.vertices, self.indices = self.create_sphere(radius, slices, stacks)
        self.init_vbo()

        # Check if there are available light IDs
        if not LightSphere.available_light_ids:
            print("Warning: Exceeded maximum number of lights supported by OpenGL")
            return

        # Assign a unique light ID
        self.light_id = LightSphere.available_light_ids.pop(0)

        # Enable the light
        glEnable(self.light_id)

        # Configure the light on creation
        self.update_light()

    def create_sphere(self, radius, slices, stacks):
        vertices = []
        indices = []

        # Generate vertices and indices for the sphere
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_TRUE)

        # Draw the sphere into a buffer to get the vertices and indices
        gluSphere(quadric, radius, slices, stacks)
        gluDeleteQuadric(quadric)

        return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

    def init_vbo(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_indices)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

    def update_light(self):
        if hasattr(self, 'light_id'):
            # Update the light's position and intensity
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

        # Armazena a cor anterior
        previous_color = glGetFloatv(GL_CURRENT_COLOR)

        if self.selected:
            glColor3f(1.0, 0.5, 0.0)
        else:
            glColor3f(*previous_color[:3])  # Restaurar a cor anterior, caso não esteja selecionado

        # Draw the sphere using the GLU function
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_FALSE)

        gluSphere(quadric, self.radius, self.slices, self.stacks)
        gluDeleteQuadric(quadric)

        # Restaura a cor anterior
        glColor3f(*previous_color[:3])
        
        glPopMatrix()

        # Update the light after drawing the object
        self.update_light()

    def to_dict(self):
        return {
            'type': 'light_sphere',
            'position': self.position,
            'radius': self.radius,
            'intensity': self.intensity,
            'color': self.color,
            'selected': self.selected  # Add 'selected' to the dictionary
        }

    @classmethod
    def from_dict(cls, data):
        radius = data['radius']
        intensity = data['intensity']
        color = data['color']
        selected = data.get('selected', False)  # Add 'selected' to the loading
        light_sphere = cls(radius=radius, intensity=intensity, color=color)
        light_sphere.position = data['position']
        light_sphere.selected = selected  # Set 'selected'
        return light_sphere

    def delete(self):
        if not hasattr(self, 'light_id'):
            return

        print(f"Deleting light: {self.light_id}")  # Debug print

        # Reset the position and intensity of the light to ensure it no longer affects the scene
        zero_position = [0.0, 0.0, 0.0, 1.0]
        zero_color = [0.0, 0.0, 0.0, 0.0]
        
        glLightfv(self.light_id, GL_POSITION, zero_position)
        glLightfv(self.light_id, GL_DIFFUSE, zero_color)
        glLightfv(self.light_id, GL_SPECULAR, zero_color)
        glLightfv(self.light_id, GL_AMBIENT, zero_color)

        # Ensure attenuation is zeroed
        glLightf(self.light_id, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(self.light_id, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(self.light_id, GL_QUADRATIC_ATTENUATION, 0.0)

        # Disable the light
        glDisable(self.light_id)

        # Return the light ID to the available pool
        LightSphere.available_light_ids.append(self.light_id)

        # Delete VBO buffers associated with the object
        glDeleteBuffers(1, [self.vbo_vertices])
        glDeleteBuffers(1, [self.vbo_indices])
