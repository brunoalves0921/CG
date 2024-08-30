import json
import os
import pygame
from objects import Mesh, Cube, Sphere, Cone, Cylinder, HalfSphere, Pyramid, LightSphere, Plane
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

        #cor de fundo do cenário
        glClearColor(0.53, 0.81, 0.98, 1.0)
        
        #habilita o teste de profundidade
        glEnable(GL_DEPTH_TEST)
        glEnableClientState(GL_VERTEX_ARRAY)
        
        #habilita a iluminação
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        #habilita a luz ambiente (luz branca do sol)
        self.sunlight_enabled = False
        self.setup_sunlight()
        
        #inicializa a câmera
        self.camera = Camera()
        self.overview_camera = Camera()
        self.eventListener = EventListener(self)
        self.show_overview = False

        #inicializa a barra lateral
        self.sidebar = Sidebar()

        #inicializa o relógio e a taxa de atualização da FPS
        self.clock = pygame.time.Clock()
        self.fps = 0
        self.fps_display_timer = pygame.time.get_ticks()
        self.fps_interval = 500  # Atualizar a FPS a cada 1000 ms (1 segundo)

        #toggle sombras
        self.render_shadows_flag = False

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
            if obj_data['type'] == 'plane':
                obj = Plane.from_dict(obj_data)
            elif obj_data['type'] == 'cube':
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
        if object_type == 'plane':
            obj = Plane()
        elif object_type == 'cube':
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

    def render_shadows(self):
        if not any(isinstance(obj, LightSphere) for obj in self.objects) and not self.sunlight_enabled:
            return  # Não renderiza sombras se não houver nenhuma luz na cena

        glPushAttrib(GL_LIGHTING_BIT | GL_TEXTURE_BIT)  # Salva o estado das configurações de iluminação e texturas
        glDisable(GL_LIGHTING)  # Desativa a iluminação
        glDisable(GL_TEXTURE_2D)  # Desativa texturas

        lights = [obj for obj in self.objects if isinstance(obj, LightSphere)]
        if self.sunlight_enabled:
            sunlight_dir = self.sunlight_position[:3]  # Obtenha a direção do Sunlight
            lights.append(('Sunlight', sunlight_dir))

        for light in lights:
            if isinstance(light, tuple) and light[0] == 'Sunlight':
                # Usa a direção do Sunlight sem modificação
                light_dir = light[1]
            else:
                # Para LightSphere, calcula a direção da luz com base na posição relativa entre a luz e o objeto
                light_pos = light.position[:3]

            for obj in self.objects:
                if isinstance(obj, Plane) or isinstance(obj, LightSphere):
                    continue  # Pula a renderização da sombra para objetos do tipo Plane e LightSphere

                # Posição do objeto
                obj_pos = obj.position[:3]

                if isinstance(light, LightSphere):
                    # Para LightSphere, calcula a direção da luz do LightSphere para o objeto
                    light_dir = [obj_pos[i] - light_pos[i] for i in range(3)]
                    # Inverta a direção da luz para que as sombras apontem na direção oposta à luz
                    light_dir = [-d for d in light_dir]
                elif isinstance(light, tuple) and light[0] == 'Sunlight':
                    # Mantém a direção original para o Sunlight, não inverte
                    light_dir = sunlight_dir

                # Verifica se a soma das componentes é diferente de zero antes de normalizar
                magnitude = sum([d**2 for d in light_dir]) ** 0.5
                if magnitude != 0:
                    light_dir = [d / magnitude for d in light_dir]  # Normaliza a direção da luz
                else:
                    # Define uma direção padrão caso a direção da luz seja zero
                    light_dir = [0, -1, 0]  # Exemplo: luz apontando para baixo

                # Limita os valores de light_dir para evitar problemas de overflow ou sombras longe demais
                light_dir = [max(min(d, 1.0), -1.0) for d in light_dir]

                shadow_matrix = [
                    1, 0, 0, 0,
                    -light_dir[0], 0, -light_dir[2], 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1
                ]

                glPushMatrix()
                glTranslatef(0, 0.01, 0)  # Adiciona uma pequena translação vertical para levantar a sombra
                glMultMatrixf(shadow_matrix)  # Aplica a matriz de sombra

                obj.draw(is_shadow=True)  # Desenha o objeto como sombra

                glPopMatrix()

        glPopAttrib()  # Restaura o estado das configurações de iluminação e texturas

    def run(self):
        self.eventListener.run()
        
        # Limpa o buffer de cor e de profundidade
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Configuração da projeção para a cena principal
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 10000.0)
        
        # Configurações da câmera principal
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(self.camera.position[0], self.camera.position[1], self.camera.zoom)
        glRotatef(self.camera.rotation[0], 1, 0, 0)
        glRotatef(self.camera.rotation[1], 0, 1, 0)
        
        # Desenha o cenário principal
        draw_axes()

        while not self.message_queue.empty():
            object_type = self.message_queue.get()
            self.add_object(object_type)

        # Atualiza e aplica a iluminação do sol
        if self.sunlight_enabled:
            glEnable(GL_LIGHT1)
            glLightfv(GL_LIGHT1, GL_POSITION, self.sunlight_position)

        # Desenha todos os objetos da cena principal
        for obj in self.objects:
            obj.draw()

        # Renderiza as sombras se o flag estiver ativado
        if self.render_shadows_flag:
            self.render_shadows()

        # Desenha o overview após o cenário principal
        if self.show_overview:
            self.draw_overview()

        # Configurações para a barra lateral
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
        
        # Atualiza o FPS periodicamente
        current_time = pygame.time.get_ticks()
        if current_time - self.fps_display_timer >= self.fps_interval:
            self.fps = self.clock.get_fps()
            self.fps_display_timer = current_time

        self.display_fps()
        
        # Atualiza a tela
        pygame.display.flip()
        self.clock.tick(999)

    def draw_overview(self):
        # Salva o estado atual do OpenGL, incluindo viewport e outros atributos
        glPushAttrib(GL_VIEWPORT_BIT | GL_TRANSFORM_BIT | GL_ENABLE_BIT | GL_LIGHTING_BIT)

        # Dimensões da janela de overview
        width, height = self.display
        overview_width = 320
        overview_height = 180
        overview_x = width - overview_width - 10
        overview_y = height - overview_height - 10

        # Configurações de projeção para a moldura
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Desenha a moldura ao redor do overview
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

        # Configura a viewport para a janela de overview
        glViewport(overview_x, overview_y, overview_width, overview_height)

        # Habilita o teste de profundidade
        glEnable(GL_DEPTH_TEST)

        # Configurações de projeção para o overview
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        # Corrige a proporção de aspecto para o overview
        aspect_ratio = overview_width / overview_height
        gluPerspective(45, aspect_ratio, 0.1, 10000.0)

        # Ajustes da câmera para o overview
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Configure a câmera de overview com parâmetros corretos
        glTranslatef(self.overview_camera.position[0], self.overview_camera.position[1], self.overview_camera.zoom)
        glRotatef(self.overview_camera.rotation[0], 1, 0, 0)
        glRotatef(self.overview_camera.rotation[1], 0, 1, 0)

        if self.sunlight_enabled:
            glEnable(GL_LIGHT1)
            glLightfv(GL_LIGHT1, GL_POSITION, self.sunlight_position)

        # Desenha os objetos no overview
        for obj in self.objects:
            obj.draw()

        # Restaura as matrizes de projeção e modelview
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        # Restaura o estado salvo do OpenGL
        glPopAttrib()

    def select_object(self, x, y):
        buffer_size = len(self.objects) * 4 * 4
        glSelectBuffer(buffer_size)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        viewport = glGetIntegerv(GL_VIEWPORT)
        gluPickMatrix(x, viewport[3] - y, 1, 1, viewport)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 10000.0)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(self.camera.position[0], self.camera.position[1], self.camera.zoom)
        glRotatef(self.camera.rotation[0], 1, 0, 0)
        glRotatef(self.camera.rotation[1], 0, 1, 0)

        for i, obj in enumerate(self.objects):
            glLoadName(i + 1)
            obj.draw()

        glPopMatrix()  # Pop do MODELVIEW
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()  # Pop do PROJECTION

        glMatrixMode(GL_MODELVIEW)
        glFlush()

        hits = glRenderMode(GL_RENDER)
        if hits:
            selected_index = self.find_closest_object(hits)
            print(f"Selected object index: {selected_index}")
            if selected_index is not None:
                print(f"Selected object: {self.objects[selected_index].__class__.__name__}")
                return int(selected_index)
        return None

    def find_closest_object(self, hits):
        min_distance = float('inf')
        closest_index = None

        for hit in hits:
            z_min = hit[1]
            names = hit[2]  # 'names' é uma lista de nomes
            if z_min < min_distance and names:
                min_distance = z_min
                closest_index = names[0] - 1  # Ajuste para indexação correta

        return closest_index

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