from OpenGL.GL import *
from OpenGL.GLU import *

def draw_cone(base, height, slices, stacks):
    quadric = gluNewQuadric()
    gluCylinder(quadric, base, 0, height, slices, stacks)
    gluDeleteQuadric(quadric)

def draw_arrow():
    # Desenhar uma seta para o eixo X (vermelho)
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(10, 0, 0)
    glRotatef(90, 0, 1, 0)
    draw_cone(0.1, 0.5, 20, 20)
    glPopMatrix()

    # Desenhar uma seta para o eixo Y (verde)
    glPushMatrix()
    glColor3f(0, 1, 0)
    glTranslatef(0, 10, 0)
    glRotatef(-90, 1, 0, 0)
    draw_cone(0.1, 0.5, 20, 20)
    glPopMatrix()

    # Desenhar uma seta para o eixo Z (azul)
    glPushMatrix()
    glColor3f(0, 0, 1)
    glTranslatef(0, 0, 10)
    draw_cone(0.1, 0.5, 20, 20)
    glPopMatrix()

def draw_axes():
    glBegin(GL_LINES)
    
    # Eixo X em vermelho
    glColor3f(1, 0, 0)
    glVertex3f(-10, 0, 0)
    glVertex3f(10, 0, 0)
    
    # Eixo Y em verde
    glColor3f(0, 1, 0)
    glVertex3f(0, -10, 0)
    glVertex3f(0, 10, 0)
    
    # Eixo Z em azul
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, -10)
    glVertex3f(0, 0, 10)
    
    glEnd()

    # Desenhando marcas de medida nos eixos
    glBegin(GL_LINES)
    for i in range(-10, 11):
        if i == 0:
            continue
        # Marcas no eixo X
        glColor3f(1, 0, 0)
        glVertex3f(i, 0.1, 0)
        glVertex3f(i, -0.1, 0)
        
        # Marcas no eixo Y
        glColor3f(0, 1, 0)
        glVertex3f(0.1, i, 0)
        glVertex3f(-0.1, i, 0)
        
        # Marcas no eixo Z
        glColor3f(0, 0, 1)
        glVertex3f(0, 0.1, i)
        glVertex3f(0, -0.1, i)
    
    glEnd()

    # Desenhar as setas nas pontas dos eixos
    draw_arrow()
