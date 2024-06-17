import pygame
from utils.camera import Camera
from utils.event_listener import EventListener
from objects import Object, Cube, Sphere, Cone, HalfSphere, Pyramid, Cylinder
from objects.eixos import draw_axes
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluPickMatrix


class Scene:
    def __init__(self):
        self.objects = []
        pygame.init()
        self.display = (1280, 720)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)

        self.camera = Camera()
        self.overview_camera = Camera()  # Câmera para o overview
        self.objects = [Cube(), Sphere(), Cone(), HalfSphere(), Pyramid(), Cylinder()]
        self.objects[0].position = [0, 0, 0]
        self.objects[1].position = [3, 0, 0]
        self.objects[2].position = [-3, 0, 0]
        self.objects[3].position = [0, 3, 0]
        self.objects[4].position = [0, -3, 0]
        self.objects[5].position = [0, 0, 3]


        self.eventListener = EventListener(self)
        self.show_overview = False  # Adiciona atributo para controlar a visibilidade do overview
    
    def start_main_loop(self):
        while True:
            self.run()

    def run(self):
        self.eventListener.run()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glTranslatef(self.camera.position[0], self.camera.position[1], self.camera.zoom)
        glPushMatrix()
        glRotatef(self.camera.rotation[0], 1, 0, 0)
        glRotatef(self.camera.rotation[1], 0, 1, 0)
        draw_axes()

        for obj in self.objects:
            obj.draw()

        glPopMatrix()

        # Desenhar visão de overview se show_overview for True
        if self.show_overview:
            # Atualizar a câmera do overview
            self.draw_overview()

        pygame.display.flip()
        pygame.time.wait(10)

    def draw_overview(self):
        # Salvar o estado atual das configurações do OpenGL
        glPushAttrib(GL_VIEWPORT_BIT | GL_TRANSFORM_BIT)
        
        # Dimensões do overview
        width, height = self.display
        overview_width = 320
        overview_height = 180
        overview_x = width - overview_width - 10
        overview_y = height - overview_height - 10
        
        # Desenhar a moldura
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glColor3f(1, 1, 1)  # Cor branca para a moldura
        glBegin(GL_LINE_LOOP)
        glVertex2f(overview_x - 5, overview_y - 5)
        glVertex2f(overview_x + overview_width + 5, overview_y - 5)
        glVertex2f(overview_x + overview_width + 5, overview_y + overview_height + 5)
        glVertex2f(overview_x - 5, overview_y + overview_height + 5)
        glEnd()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        # Configurar o viewport para a pequena janela no canto superior direito
        glViewport(overview_x, overview_y, overview_width, overview_height)
        
        # Configurar a matriz de projeção para a visão overview
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(45, overview_width / overview_height, 0.1, 50.0)
        
        # Configurar a matriz de modelo para a visão overview
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(self.overview_camera.position[0], self.overview_camera.position[1], self.overview_camera.zoom)
        glRotatef(self.overview_camera.rotation[0], 1, 0, 0)
        glRotatef(self.overview_camera.rotation[1], 0, 1, 0)

        # Desenhar todos os objetos na visão overview
        draw_axes()
        for obj in self.objects:
            obj.draw()

        # Restaurar as configurações do OpenGL
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()

    def select_object(self, x, y):
        buffer_size = 512
        select_buffer = glSelectBuffer(buffer_size)
        glRenderMode(GL_SELECT)

        glInitNames()
        glPushName(0)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        viewport = glGetIntegerv(GL_VIEWPORT)
        gluPickMatrix(x, viewport[3] - y, 1, 1, viewport)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)

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
        if type(hits) == list:
            hits = len(hits)

        if hits > 0:
            return select_buffer[:hits * 4]
        else:
            return []
