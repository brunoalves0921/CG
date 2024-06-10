import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from objects.cubo import Cube
from objects.eixos import draw_axes
from OBJFileLoader import OBJ

def main():
    pygame.init()
    display = (1280, 960)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    # Fundo branco
    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)  # Habilitar teste de profundidade

    rotation = [0, 0]
    last_pos = None
    zoom = -5  # Variável para controlar o zoom

    # Criar uma instância de Cube
    cube = Cube()
    # model = OBJ('objects/Male.obj', swapyz=True, default_mtl=('objects/cube.mtl', 'Material'))

    rotate_mode = False  # Variável para controlar o modo de rotação
    translate_mode = False  # Variável para controlar o modo de translação

    while True:
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
                if event.button == 1:  # Botão esquerdo do mouse
                    last_pos = pygame.mouse.get_pos()
                elif event.button == 4:  # Scroll para cima
                    if rotate_mode:
                        if ctrl_pressed:
                            cube.rotate(5, (1, 0, 0))  # Rotaciona no eixo X
                        elif shift_pressed:
                            cube.rotate(5, (0, 1, 0))  # Rotaciona no eixo Y
                        elif alt_pressed:
                            cube.rotate(5, (0, 0, 1))  # Rotaciona no eixo Z
                    elif translate_mode:
                        if ctrl_pressed:
                            cube.translate(0.1, (1, 0, 0))  # Translada no eixo X
                        elif shift_pressed:
                            cube.translate(0.1, (0, 1, 0))  # Translada no eixo Y
                        elif alt_pressed:
                            cube.translate(0.1, (0, 0, 1))  # Translada no eixo Z
                    else:
                        if ctrl_pressed and shift_pressed and alt_pressed: 
                            cube.scale(0.05, (1, 0, 0))  # Escalona uniformemente
                            cube.scale(0.05, (0, 1, 0))
                            cube.scale(0.05, (0, 0, 1))
                        elif ctrl_pressed:
                            cube.scale(0.05, (1, 0, 0))  # Escalona no eixo X
                        elif shift_pressed:
                            cube.scale(0.05, (0, 1, 0))  # Escalona no eixo Y
                        elif alt_pressed:
                            cube.scale(0.05, (0, 0, 1))  # Escalona no eixo Z
                        else:
                            zoom += 0.5  # Aumentar zoom (aproximar)
                elif event.button == 5:  # Scroll para baixo
                    if rotate_mode:
                        if ctrl_pressed:
                            cube.rotate(-5, (1, 0, 0))  # Rotaciona no eixo X
                        elif shift_pressed:
                            cube.rotate(-5, (0, 1, 0))  # Rotaciona no eixo Y
                        elif alt_pressed:
                            cube.rotate(-5, (0, 0, 1))  # Rotaciona no eixo Z
                    elif translate_mode:
                        if ctrl_pressed:
                            cube.translate(-0.1, (1, 0, 0))  # Translada no eixo X
                        elif shift_pressed:
                            cube.translate(-0.1, (0, 1, 0))  # Translada no eixo Y
                        elif alt_pressed:
                            cube.translate(-0.1, (0, 0, 1))  # Translada no eixo Z
                    else:
                        if ctrl_pressed and shift_pressed and alt_pressed:
                            cube.scale(-0.05, (1, 0, 0))  # Escalona uniformemente
                            cube.scale(-0.05, (0, 1, 0))
                            cube.scale(-0.05, (0, 0, 1))
                        elif ctrl_pressed:
                            cube.scale(-0.05, (1, 0, 0))  # Escalona no eixo X
                        elif shift_pressed:
                            cube.scale(-0.05, (0, 1, 0))  # Escalona no eixo Y
                        elif alt_pressed:
                            cube.scale(-0.05, (0, 0, 1))  # Escalona no eixo Z
                        else:
                            zoom -= 0.5  # Diminuir zoom (afastar)
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

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, zoom)
        glPushMatrix()
        glRotatef(rotation[0], 1, 0, 0)
        glRotatef(rotation[1], 0, 1, 0)
        draw_axes()  # Desenhar o plano cartesiano
        cube.draw()  # Desenhar o cubo
        # model.render() #RENDERIZAR O OBJETO
        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
