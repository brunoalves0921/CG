import pygame
from utils.camera import Camera
from utils.event_listener import EventListener
from objects import Object, Cube, Sphere
from objects.eixos import draw_axes
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluPickMatrix


class Scene:
    def __init__(self):
        self.objects: list[Object] = []
        # Inicialização do Pygame e configuração da janela
        pygame.init()
        self.display = (1280, 720)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)
        glClearColor(1, 1, 1, 1)
        glEnable(GL_DEPTH_TEST)

        self.camera = Camera()

        # Criação de uma lista de objetos (cubos e esferas)
        self.objects = [Cube(), Cube(), Cube(), Sphere()]
        self.objects[1].position = [3, 0, 0]
        self.objects[2].position = [-3, 0, 0]
        self.objects[3].position = [0, 3, 0]  # Adiciona uma esfera

        self.eventListener = EventListener(self)
    
    def start_main_loop(self):
        while True:
            self.run()

    def run(self):
        self.eventListener.run()

        # Limpar o buffer de cor e profundidade
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glTranslatef(self.camera.position[0], self.camera.position[1], self.camera.zoom)
        glPushMatrix()
        glRotatef(self.camera.rotation[0], 1, 0, 0)
        glRotatef(self.camera.rotation[1], 0, 1, 0)
        draw_axes()

        # Desenhar todos os objetos
        for obj in self.objects:
            obj.draw()

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

    def select_object(self, x, y):
        """
        Função para selecionar um objeto usando um raio a partir das coordenadas do mouse.
        """
        buffer_size = 512
        select_buffer = glSelectBuffer(buffer_size)
        glRenderMode(GL_SELECT)

        # Inicializar os nomes para seleção
        glInitNames()
        glPushName(0)

        # Configurar a matriz de projeção para seleção
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

        # Desenhar todos os objetos para seleção
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
