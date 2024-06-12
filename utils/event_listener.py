import pygame
from pygame.locals import KMOD_CTRL, KMOD_SHIFT, KMOD_ALT, K_r, K_t

class EventListener:
    def __init__(self, scene):
        self.scene = scene
        self.last_pos = None
        self.rotate_mode = False
        self.translate_mode = False
    
    def run(self):
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
                    self.rotate_mode = True
                elif event.key == K_t:
                    self.translate_mode = True
            elif event.type == pygame.KEYUP:
                if event.key == K_r:
                    self.rotate_mode = False
                elif event.key == K_t:
                    self.translate_mode = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    hits = self.scene.select_object(x, y)
                    if len(hits) > 0:
                        # Obter o índice do cubo selecionado
                        selected_cube_index = hits[3] - 1
                        if self.scene.objects[selected_cube_index].selected:
                            self.scene.objects[selected_cube_index].selected = False
                        else:
                            if not shift_pressed:
                                # Desselcionar todos os cubos antes de selecionar o novo, exceto se Shift estiver pressionado
                                for cube in self.scene.objects:
                                    cube.selected = False
                            self.scene.objects[selected_cube_index].selected = True
                    self.last_pos = pygame.mouse.get_pos()
                elif event.button == 3:
                    self.last_pos = pygame.mouse.get_pos()
                elif event.button == 4:  # Scroll up
                    if any(cube.selected for cube in self.scene.objects):
                        for cube in self.scene.objects:
                            if cube.selected:
                                if ctrl_pressed:
                                    if self.rotate_mode:
                                        cube.rotate(5, (1, 0, 0))
                                    elif self.translate_mode:
                                        cube.translate(0.1, (1, 0, 0))
                                    else:
                                        cube.scale(0.05, (1, 0, 0))
                                if shift_pressed:
                                    if self.rotate_mode:
                                        cube.rotate(5, (0, 1, 0))
                                    elif self.translate_mode:
                                        cube.translate(0.1, (0, 1, 0))
                                    else:
                                        cube.scale(0.05, (0, 1, 0))
                                if alt_pressed:
                                    if self.rotate_mode:
                                        cube.rotate(5, (0, 0, 1))
                                    elif self.translate_mode:
                                        cube.translate(0.1, (0, 0, 1))
                                    else:
                                        cube.scale(0.05, (0, 0, 1))
                    else:
                        self.scene.camera.zoom += 0.5
                elif event.button == 5:  # Scroll down
                    if any(cube.selected for cube in self.scene.objects):
                        for cube in self.scene.objects:
                            if cube.selected:
                                if ctrl_pressed:
                                    if self.rotate_mode:
                                        cube.rotate(-5, (1, 0, 0))
                                    elif self.translate_mode:
                                        cube.translate(-0.1, (1, 0, 0))
                                    else:
                                        cube.scale(-0.05, (1, 0, 0))
                                if shift_pressed:
                                    if self.rotate_mode:
                                        cube.rotate(-5, (0, 1, 0))
                                    elif self.translate_mode:
                                        cube.translate(-0.1, (0, 1, 0))
                                    else:
                                        cube.scale(-0.05, (0, 1, 0))
                                if alt_pressed:
                                    if self.rotate_mode:
                                        cube.rotate(-5, (0, 0, 1))
                                    elif self.translate_mode:
                                        cube.translate(-0.1, (0, 0, 1))
                                    else:
                                        cube.scale(-0.05, (0, 0, 1))
                    else:
                        self.scene.camera.zoom -= 0.5
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 or event.button == 3:
                    self.last_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.last_pos:
                    x, y = pygame.mouse.get_pos()
                    dx = x - self.last_pos[0]
                    dy = y - self.last_pos[1]
                    if event.buttons[2]:  # Botão direito do mouse
                        self.scene.camera.position[0] += dx * 0.01
                        self.scene.camera.position[1] -= dy * 0.01
                    else:  # Botão esquerdo do mouse
                        self.scene.camera.rotation[0] += dy
                        self.scene.camera.rotation[1] += dx
                    self.last_pos = (x, y)
