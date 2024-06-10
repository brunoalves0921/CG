import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from objects.cubo import Cube
from objects.eixos import draw_axes

def get_ray_from_mouse(x, y, display):
    """
    Função para calcular um raio a partir das coordenadas do mouse.
    """
    # Coordenadas normalizadas do dispositivo (NDC)
    ndc_x = (2.0 * x) / display[0] - 1.0
    ndc_y = 1.0 - (2.0 * y) / display[1]
    ndc_z = 1.0
    ray_ndc = np.array([ndc_x, ndc_y, -ndc_z, 1.0])

    # Obter as matrizes de projeção e visualização atuais
    projection_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
    view_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)

    # Calcular o inverso das matrizes de projeção e visualização
    inverse_projection_matrix = np.linalg.inv(projection_matrix)
    inverse_view_matrix = np.linalg.inv(view_matrix)

    # Transformar as coordenadas do raio do espaço de recorte para o espaço mundial
    ray_clip = np.dot(inverse_projection_matrix, ray_ndc)
    ray_clip = ray_clip / ray_clip[3]
    ray_world = np.dot(inverse_view_matrix, ray_clip)
    ray_world = ray_world / ray_world[3]

    # Calcular a origem e a direção do raio no espaço mundial
    ray_origin = np.array(inverse_view_matrix[:, 3][:3])
    ray_direction = ray_world[:3] - ray_origin
    ray_direction = ray_direction / np.linalg.norm(ray_direction)

    return ray_origin, ray_direction

def select_object(x, y, display, cubes):
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
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, zoom)
    glPushMatrix()
    glRotatef(rotation[0], 1, 0, 0)
    glRotatef(rotation[1], 0, 1, 0)
    draw_axes()

    # Desenhar todos os cubos para seleção
    for i, cube in enumerate(cubes):
        glLoadName(i + 1)
        cube.draw()
    
    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glFlush()

    hits = glRenderMode(GL_RENDER)
    return hits

def main():
    # Inicialização do Pygame e configuração da janela
    pygame.init()
    display = (1280, 960)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)

    global rotation, last_pos, zoom
    rotation = [0, 0]
    last_pos = None
    zoom = -5

    # Criação de uma lista de cubos
    cubes = [Cube(), Cube(), Cube()]
    cubes[1].position = [3, 0, 0]
    cubes[2].position = [-3, 0, 0]

    rotate_mode = False
    translate_mode = False

    while True:
        # Verificar estado das teclas modificadoras
        ctrl_pressed = pygame.key.get_mods() & KMOD_CTRL
        shift_pressed = pygame.key.get_mods() & KMOD_SHIFT
        alt_pressed = pygame.key.get_mods() & KMOD_ALT

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_r:
                    rotate_mode = True
                elif event.key == K_t:
                    translate_mode = True
            elif event.type == pygame.KEYUP:
                if event.key == K_r:
                    rotate_mode = False
                elif event.key == K_t:
                    translate_mode = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    hits = select_object(x, y, display, cubes)
                    if hits:
                        selected_cube_index = hits[0][2][0] - 1
                        if cubes[selected_cube_index].selected:
                            cubes[selected_cube_index].selected = False
                        else:
                            if not shift_pressed:
                                # Desselcionar todos os cubos antes de selecionar o novo, exceto se Shift estiver pressionado
                                for cube in cubes:
                                    cube.selected = False
                            cubes[selected_cube_index].selected = True
                    last_pos = pygame.mouse.get_pos()
                elif event.button == 4:  # Scroll up
                    if any(cube.selected for cube in cubes):
                        for cube in cubes:
                            if cube.selected:
                                if ctrl_pressed and shift_pressed and alt_pressed:
                                    cube.scale(0.05, (1, 0, 0))
                                    cube.scale(0.05, (0, 1, 0))
                                    cube.scale(0.05, (0, 0, 1))
                                elif ctrl_pressed:
                                    if rotate_mode:
                                        cube.rotate(-5, (1, 0, 0))
                                    elif translate_mode:
                                        cube.translate(0.1, (1, 0, 0))
                                    else:
                                        cube.scale(0.05, (1, 0, 0))
                                elif shift_pressed:
                                    if rotate_mode:
                                        cube.rotate(-5, (0, 1, 0))
                                    elif translate_mode:
                                        cube.translate(0.1, (0, 1, 0))
                                    else:
                                        cube.scale(0.05, (0, 1, 0))
                                elif alt_pressed:
                                    if rotate_mode:
                                        cube.rotate(-5, (0, 0, 1))
                                    elif translate_mode:
                                        cube.translate(0.1, (0, 0, 1))
                                    else:
                                        cube.scale(0.05, (0, 0, 1))
                                else:
                                    cube.scale(0.05, (1, 1, 1))
                    else:
                        zoom += 0.5
                elif event.button == 5:  # Scroll down
                    if any(cube.selected for cube in cubes):
                        for cube in cubes:
                            if cube.selected:
                                if ctrl_pressed and shift_pressed and alt_pressed:
                                    cube.scale(-0.05, (1, 0, 0))
                                    cube.scale(-0.05, (0, 1, 0))
                                    cube.scale(-0.05, (0, 0, 1))
                                elif ctrl_pressed:
                                    if rotate_mode:
                                        cube.rotate(5, (1, 0, 0))
                                    elif translate_mode:
                                        cube.translate(-0.1, (1, 0, 0))
                                    else:
                                        cube.scale(-0.05, (1, 0, 0))
                                elif shift_pressed:
                                    if rotate_mode:
                                        cube.rotate(5, (0, 1, 0))
                                    elif translate_mode:
                                        cube.translate(-0.1, (0, 1, 0))
                                    else:
                                        cube.scale(-0.05, (0, 1, 0))
                                elif alt_pressed:
                                    if rotate_mode:
                                        cube.rotate(5, (0, 0, 1))
                                    elif translate_mode:
                                        cube.translate(-0.1, (0, 0, 1))
                                    else:
                                        cube.scale(-0.05, (0, 0, 1))
                                else:
                                    cube.scale(-0.05, (1, 1, 1))
                    else:
                        zoom -= 0.5
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    last_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if last_pos:
                    x, y = pygame.mouse.get_pos()
                    dx = x - last_pos[0]
                    dy = y - last_pos[1]
                    rotation[0] += dy
                    rotation[1] += dx
                    last_pos = (x, y)

        # Limpar o buffer de cor e profundidade
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, zoom)
        glPushMatrix()
        glRotatef(rotation[0], 1, 0, 0)
        glRotatef(rotation[1], 0, 1, 0)
        draw_axes()

        # Desenhar todos os cubos
        for cube in cubes:
            cube.draw()

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
