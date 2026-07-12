import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Vertices of a square plane
vertices = (
    (-5, 0, -5),
    (5, 0, -5),
    (5, 0, 5),
    (-5, 0, 5)
)

edges = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0)
)

def draw_plane():
    # Filled plane
    glColor3f(0.75, 0.75, 0.75)
    glBegin(GL_QUADS)
    for vertex in vertices:
        glVertex3fv(vertex)
    glEnd()

    # Outline
    glColor3f(0, 0, 0)
    glLineWidth(2)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_axes():
    glLineWidth(3)

    # X axis (Red)
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(10, 0, 0)
    glEnd()

    # Y axis (Green)
    glBegin(GL_LINES)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 10, 0)
    glEnd()

    # Z axis (Blue)
    glBegin(GL_LINES)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 10)
    glEnd()

pygame.init()

display = (1000, 700)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("Simple 3D Plane")

gluPerspective(45, display[0] / display[1], 0.1, 100.0)

glTranslatef(0, -2, -20)

rot_x = 25
rot_y = -30

dragging = False
last_mouse = (0, 0)

clock = pygame.time.Clock()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True
                last_mouse = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            x, y = pygame.mouse.get_pos()
            dx = x - last_mouse[0]
            dy = y - last_mouse[1]

            rot_y += dx * 0.5
            rot_x += dy * 0.5

            last_mouse = (x, y)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glPushMatrix()

    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 1, 0)

    draw_axes()
    draw_plane()

    glPopMatrix()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()