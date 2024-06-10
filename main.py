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
    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)

    rotation = [0, 0]
    last_pos = None
    zoom = -5

    cube = Cube()

    rotate_mode = False
    translate_mode = False

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
                if event.button == 1:
                    last_pos = pygame.mouse.get_pos()
                elif event.button == 4:
                    if rotate_mode:
                        if ctrl_pressed:
                            cube.rotate(5, (1, 0, 0))
                        elif shift_pressed:
                            cube.rotate(5, (0, 1, 0))
                        elif alt_pressed:
                            cube.rotate(5, (0, 0, 1))
                    elif translate_mode:
                        if ctrl_pressed:
                            cube.translate(0.1, (1, 0, 0))
                        elif shift_pressed:
                            cube.translate(0.1, (0, 1, 0))
                        elif alt_pressed:
                            cube.translate(0.1, (0, 0, 1))
                    else:
                        if ctrl_pressed and shift_pressed and alt_pressed:
                            cube.scale(0.05, (1, 0, 0))
                            cube.scale(0.05, (0, 1, 0))
                            cube.scale(0.05, (0, 0, 1))
                        elif ctrl_pressed:
                            cube.scale(0.05, (1, 0, 0))
                        elif shift_pressed:
                            cube.scale(0.05, (0, 1, 0))
                        elif alt_pressed:
                            cube.scale(0.05, (0, 0, 1))
                        else:
                            zoom += 0.5
                elif event.button == 5:
                    if rotate_mode:
                        if ctrl_pressed:
                            cube.rotate(-5, (1, 0, 0))
                        elif shift_pressed:
                            cube.rotate(-5, (0, 1, 0))
                        elif alt_pressed:
                            cube.rotate(-5, (0, 0, 1))
                    elif translate_mode:
                        if ctrl_pressed:
                            cube.translate(-0.1, (1, 0, 0))
                        elif shift_pressed:
                            cube.translate(-0.1, (0, 1, 0))
                        elif alt_pressed:
                            cube.translate(-0.1, (0, 0, 1))
                    else:
                        if ctrl_pressed and shift_pressed and alt_pressed:
                            cube.scale(-0.05, (1, 0, 0))
                            cube.scale(-0.05, (0, 1, 0))
                            cube.scale(-0.05, (0, 0, 1))
                        elif ctrl_pressed:
                            cube.scale(-0.05, (1, 0, 0))
                        elif shift_pressed:
                            cube.scale(-0.05, (0, 1, 0))
                        elif alt_pressed:
                            cube.scale(-0.05, (0, 0, 1))
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

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, zoom)
        glPushMatrix()
        glRotatef(rotation[0], 1, 0, 0)
        glRotatef(rotation[1], 0, 1, 0)
        draw_axes()
        cube.draw()
        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
