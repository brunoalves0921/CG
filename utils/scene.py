import json
import os
import pygame
from objects import Mesh, Cube, Sphere, Cone, Cylinder, HalfSphere, Pyramid, LightSphere
from utils.camera import Camera
from utils.event_listener import EventListener
from utils.sidebar import Sidebar
from objects.eixos import draw_axes
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective, gluPickMatrix

class Scene:
    def __init__(self, message_queue):
        self.objects = []
        self.message_queue = message_queue
        pygame.init()
        self.display = (1620, 830)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)  # Enable MSAA
        pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)  # Enable hardware acceleration
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)  # Enable double buffering
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)  # Set depth buffer size to 24 bits
        pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)  # Set alpha buffer size to 8 bits
        pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)  # Set stencil buffer size to 8 bits
        pygame.display.gl_set_attribute(pygame.GL_FRAMEBUFFER_SRGB_CAPABLE, 1)  # Enable sRGB color space
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)  # Use core profile
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 10000.0)
        glTranslatef(0.0, 0.0, -5)

        glClearColor(0.53, 0.81, 0.98, 1.0)
        
        glEnable(GL_DEPTH_TEST)
        glEnableClientState(GL_VERTEX_ARRAY)
        
        glEnable(GL_LIGHTING)
        # glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        self.sunlight_enabled = False
        self.setup_sunlight()
        
        self.camera = Camera()
        self.overview_camera = Camera()
        self.eventListener = EventListener(self)
        self.show_overview = False

        self.sidebar = Sidebar()

        self.clock = pygame.time.Clock()
        self.fps = 0

    def save_scene(self, file_path):
        scene_data = {
            'objects': [obj.to_dict() for obj in self.objects],
            'camera': self.camera.to_dict()  # Save camera position
        }
        with open(file_path, 'w') as f:
            json.dump(scene_data, f, indent=4)

    def load_scene(self, file_path):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, 'r') as f:
            scene_data = json.load(f)

        self.objects = []
        for obj_data in scene_data['objects']:
            if obj_data['type'] == 'cube':
                obj = Cube.from_dict(obj_data)
            elif obj_data['type'] == 'sphere':
                obj = Sphere.from_dict(obj_data)
            elif obj_data['type'] == 'cone':
                obj = Cone.from_dict(obj_data)
            elif obj_data['type'] == 'cylinder':
                obj = Cylinder.from_dict(obj_data)
            elif obj_data['type'] == 'halfsphere':
                obj = HalfSphere.from_dict(obj_data)
            elif obj_data['type'] == 'pyramid':
                obj = Pyramid.from_dict(obj_data)
            elif obj_data['type'] == 'light_sphere':
                obj = LightSphere.from_dict(obj_data)
            elif obj_data['type'] == 'mesh':
                obj = Mesh.from_dict(obj_data)
            else:
                print(f"Unknown object type: {obj_data['type']}")
                continue

            self.objects.append(obj)

        if 'camera' in scene_data:
            self.camera.from_dict(scene_data['camera'])  # Load camera position

    def add_object(self, object_type):
        if object_type == 'cube':
            obj = Cube()
        elif object_type == 'sphere':
            obj = Sphere()
        elif object_type == 'cone':
            obj = Cone()
        elif object_type == 'cylinder':
            obj = Cylinder()
        elif object_type == 'halfsphere':
            obj = HalfSphere()
        elif object_type == 'pyramid':
            obj = Pyramid()
        elif object_type == 'light':
            obj = LightSphere()
        else:
            print(f"Unknown object type: {object_type}")
            return

        obj.position = [0, 0, 0]
        obj.init_vbo()
        self.objects.append(obj)

    def start_main_loop(self):
        saved_scene_file = 'saved_scene.json'
        if os.path.exists(saved_scene_file):
            self.load_scene(saved_scene_file)

        while True:
            self.run()

        self.save_scene(saved_scene_file)

    def setup_sunlight(self):
        self.sunlight_position = [10.0, 10.0, 10.0, 1.0]
        self.sunlight_ambient = [0.2, 0.2, 0.2, 1.0]
        self.sunlight_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.sunlight_specular = [1.0, 1.0, 1.0, 1.0]

    def toggle_sunlight(self):
        if self.sunlight_enabled:
            glDisable(GL_LIGHT1)
        else:
            glEnable(GL_LIGHT1)
            glLightfv(GL_LIGHT1, GL_POSITION, self.sunlight_position)
            glLightfv(GL_LIGHT1, GL_AMBIENT, self.sunlight_ambient)
            glLightfv(GL_LIGHT1, GL_DIFFUSE, self.sunlight_diffuse)
            glLightfv(GL_LIGHT1, GL_SPECULAR, self.sunlight_specular)
        self.sunlight_enabled = not self.sunlight_enabled

    def run(self):
        self.eventListener.run()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 10000.0)
        glTranslatef(self.camera.position[0], self.camera.position[1], self.camera.zoom)
        glRotatef(self.camera.rotation[0], 1, 0, 0)
        glRotatef(self.camera.rotation[1], 0, 1, 0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glPushMatrix()  # Push initial modelview matrix

        # draw_axes()

        while not self.message_queue.empty():
            object_type = self.message_queue.get()
            self.add_object(object_type)
        
        if self.sunlight_enabled:
            glEnable(GL_LIGHT1)
            glLightfv(GL_LIGHT1, GL_POSITION, self.sunlight_position)

        for obj in self.objects:
            obj.draw()

        glPopMatrix()  # Pop initial modelview matrix

        if self.show_overview:
            self.draw_overview()

        glPushMatrix()  # Push matrix for sidebar
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.sidebar.draw()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # Calculate and display FPS
        self.fps = self.clock.get_fps()
        self.display_fps()

        pygame.display.flip()
        self.clock.tick(999)

    def draw_overview(self):
        glPushAttrib(GL_VIEWPORT_BIT | GL_TRANSFORM_BIT)
        width, height = self.display
        overview_width = 320
        overview_height = 180
        overview_x = width - overview_width - 10
        overview_y = height - overview_height - 10
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(1, 1, 1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(overview_x - 5, overview_y - 5)
        glVertex2f(overview_x + overview_width + 5, overview_y - 5)
        glVertex2f(overview_x + overview_width + 5, overview_y + overview_height + 5)
        glVertex2f(overview_x - 5, overview_y + overview_height + 5)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glViewport(overview_x, overview_y, overview_width, overview_height)
        # glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(45, overview_width / overview_height, 0.1, 10000.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(self.overview_camera.position[0], self.overview_camera.position[1], self.overview_camera.zoom)
        glRotatef(self.overview_camera.rotation[0], 1, 0, 0)
        glRotatef(self.overview_camera.rotation[1], 0, 1, 0)
        draw_axes()
        for obj in self.objects:
            obj.draw()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        # glMatrixMode(GL_MODELVIEW)
        glPopAttrib()

    def select_object(self, x, y):
        # Aumente o tamanho do buffer para o necessário para armazenar todos os objetos
        buffer_size = len(self.objects) * 4 * 4
        print(f"Buffer size: {buffer_size}")
        select_buffer = glSelectBuffer(buffer_size)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        viewport = glGetIntegerv(GL_VIEWPORT)
        # Diminuir a área de seleção para 1x1 pixels para maior precisão
        gluPickMatrix(x, viewport[3] - y, 1, 1, viewport)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 10000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(self.camera.position[0], self.camera.position[1], self.camera.zoom)
        
        glPushMatrix()
        glRotatef(self.camera.rotation[0], 1, 0, 0)
        glRotatef(self.camera.rotation[1], 0, 1, 0)
        draw_axes()

        for i, obj in enumerate(self.objects):
            glLoadName(i + 1)
            if isinstance(obj, Mesh):
                obj.draw()  # Draw mesh objects
            else:
                obj.draw()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glFlush()

        hits = glRenderMode(GL_RENDER)
        if isinstance(hits, list):
            hits = len(hits)
        if hits > 0:
            return select_buffer[:hits * 4]
        else:
            return []
    def delete_selected_object(self):
        # se o objeto for do tipo light_sphere, chame o método delete
        for obj in self.objects:
            if obj.selected:
                if isinstance(obj, LightSphere):
                    obj.delete()
                self.objects.remove(obj)
                break
        print(f"Deleted selected object")
        print(f"Total objects: {len(self.objects)}")

    def render_text(self, text, x, y, font_name='Arial', font_size=18):
        font = pygame.font.SysFont(font_name, font_size)
        text_surface = font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 0))
        text_data = pygame.image.tostring(text_surface, 'RGBA', True)
        width, height = text_surface.get_size()

        glRasterPos2f(x, y)
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def display_fps(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], 0, self.display[1], -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        self.render_text(f"FPS: {self.fps:.2f}", 10, self.display[1] - 30)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)