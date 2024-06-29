import json
import os
import pygame
from objects import Mesh
from utils.camera import Camera
from utils.event_listener import EventListener
from utils.sidebar import Sidebar
from objects import Cube, Sphere, Cone, Cylinder, HalfSphere, Pyramid
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
        self.display = (1920, 1030)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        glEnable(GL_MULTISAMPLE)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 10000.0)
        glTranslatef(0.0, 0.0, -5)
        glClearColor(0.53, 0.81, 0.92, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnableClientState(GL_VERTEX_ARRAY)
        
        # Configurações de iluminação
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # # Configuração da luz
        # light_position = [1, 1, 1, 0]
        # glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        # light_ambient = [0.1, 0.1, 0.1, 1.0]
        # glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        # light_diffuse = [1.0, 1.0, 1.0, 1.0]
        # glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        # light_specular = [1.0, 1.0, 1.0, 1.0]
        # glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        
        self.camera = Camera()
        self.overview_camera = Camera()
        self.eventListener = EventListener(self)
        self.show_overview = False

        self.sidebar = Sidebar()

        # FPS counter variables
        self.clock = pygame.time.Clock()
        self.fps = 0

        #self.objects.append(Mesh([0, 0, 0], 'objects/mesh/cube.obj', True))
    
    def save_scene(self, file_path):
        scene_data = {
            'objects': [obj.to_dict() for obj in self.objects]
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
            else:
                print(f"Unknown object type: {obj_data['type']}")
                continue

            self.objects.append(obj)

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
        else:
            print(f"Unknown object type: {object_type}")
            return
        print(f"Adding object: {object_type}")
        print(f"Total objects: {len(self.objects) + 1}")

        obj.position = [0, 0, 0]
        obj.init_vbo()  # Initialize VBO for the object
        self.objects.append(obj)

    def start_main_loop(self):
        while True:
            self.run()

    def run(self):
        self.eventListener.run()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 10000.0)
        glTranslatef(self.camera.position[0], self.camera.position[1], self.camera.zoom)
        glPushMatrix()
        glRotatef(self.camera.rotation[0], 1, 0, 0)
        glRotatef(self.camera.rotation[1], 0, 1, 0)
        draw_axes()

        while not self.message_queue.empty():
            object_type = self.message_queue.get()
            self.add_object(object_type)

        for obj in self.objects:
            obj.draw()

        glPopMatrix()

        if self.show_overview:
            self.draw_overview()

        # Desenhar a barra lateral
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        self.sidebar.draw()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # Calcular e exibir FPS
        self.fps = self.clock.get_fps()
        self.display_fps()

        pygame.display.flip()
        self.clock.tick(60)

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
        glMatrixMode(GL_PROJECTION)
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
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()

    def select_object(self, x, y):
        #aumente o tamanho do buffer para o necessário para armazenar todos os objetos
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
        self.objects = [obj for obj in self.objects if not obj.selected]
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
