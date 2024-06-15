import pygame
from pygame.locals import KMOD_CTRL, KMOD_SHIFT, KMOD_ALT, K_r, K_t, K_c, K_F1, K_F2, K_F3, K_F4, K_F5, K_o
from OpenGL.GL import *

class EventListener:
    def __init__(self, scene):
        self.scene = scene
        self.last_pos = None
        self.rotate_mode = False
        self.translate_mode = False
        self.shear_mode = False
    
    def run(self):
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
                elif event.key == K_c:
                    self.shear_mode = True
                elif event.key == K_F1:
                    if self.scene.show_overview:
                        self.scene.overview_camera.set_preset_position(1)
                    else:
                        self.scene.camera.set_preset_position(1)
                elif event.key == K_F2:
                    if self.scene.show_overview:
                        self.scene.overview_camera.set_preset_position(2)
                    else:
                        self.scene.camera.set_preset_position(2)
                elif event.key == K_F3:
                    if self.scene.show_overview:
                        self.scene.overview_camera.set_preset_position(3)
                    else:
                        self.scene.camera.set_preset_position(3)
                elif event.key == K_F4:
                    if self.scene.show_overview:
                        self.scene.overview_camera.set_preset_position(4)
                    else:
                        self.scene.camera.set_preset_position(4)
                elif event.key == K_F5:
                    if self.scene.show_overview:
                        self.scene.overview_camera.set_preset_position(5)
                    else:
                        self.scene.camera.set_preset_position(5)
                elif event.key == K_o:
                    self.scene.show_overview = not self.scene.show_overview  # Alterna o estado do overview
            elif event.type == pygame.KEYUP:
                if event.key == K_r:
                    self.rotate_mode = False
                elif event.key == K_t:
                    self.translate_mode = False
                elif event.key == K_c:
                    self.shear_mode = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    hits = self.scene.select_object(x, y)
                    if len(hits) > 0:
                        selected_object_index = hits[3] - 1
                        selected_object = self.scene.objects[selected_object_index]
                        if selected_object.selected:
                            selected_object.selected = False
                        else:
                            if not shift_pressed:
                                for obj in self.scene.objects:
                                    obj.selected = False
                            selected_object.selected = True
                    self.last_pos = pygame.mouse.get_pos()
                elif event.button == 3:
                    self.last_pos = pygame.mouse.get_pos()
                elif event.button in [4, 5]:
                    direction = 1 if event.button == 4 else -1
                    value_rotate = 5 * direction
                    value_translate = 0.1 * direction
                    value_scale = 0.05 * direction

                    # Limitar a escala mínima
                    min_scale = 0.1

                    if any(obj.selected for obj in self.scene.objects):
                        for obj in self.scene.objects:
                            if obj.selected:
                                if self.shear_mode:
                                    if ctrl_pressed:
                                        obj.shear(value_scale, 'xy')
                                elif ctrl_pressed:
                                    if self.rotate_mode:
                                        obj.rotate(value_rotate, (1, 0, 0))
                                    elif self.translate_mode:
                                        obj.translate(value_translate, (1, 0, 0))
                                    else:
                                        # Limitar a escala mínima
                                        if obj.transform.scale[0] + value_scale >= min_scale:
                                            obj.scale(value_scale, (1, 0, 0))
                                if shift_pressed:
                                    if self.rotate_mode:
                                        obj.rotate(value_rotate, (0, 1, 0))
                                    elif self.translate_mode:
                                        obj.translate(value_translate, (0, 1, 0))
                                    else:
                                        # Limitar a escala mínima
                                        if obj.transform.scale[1] + value_scale >= min_scale:
                                            obj.scale(value_scale, (0, 1, 0))
                                if alt_pressed:
                                    if self.rotate_mode:
                                        obj.rotate(value_rotate, (0, 0, 1))
                                    elif self.translate_mode:
                                        obj.translate(value_translate, (0, 0, 1))
                                    else:
                                        # Limitar a escala mínima
                                        if obj.transform.scale[2] + value_scale >= min_scale:
                                            obj.scale(value_scale, (0, 0, 1))
                    else:
                        if self.scene.show_overview:
                            self.scene.overview_camera.zoom += 0.5 * direction
                        else:
                            self.scene.camera.zoom += 0.5 * direction
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 or event.button == 3:
                    self.last_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.last_pos:
                    x, y = pygame.mouse.get_pos()
                    dx = x - self.last_pos[0]
                    dy = y - self.last_pos[1]
                    if event.buttons[2]:  # Botão direito do mouse
                        if self.scene.show_overview:
                            self.scene.overview_camera.position[0] += dx * 0.01
                            self.scene.overview_camera.position[1] -= dy * 0.01
                        else:
                            self.scene.camera.position[0] += dx * 0.01
                            self.scene.camera.position[1] -= dy * 0.01
                    else:  # Botão esquerdo do mouse
                        if self.scene.show_overview:
                            self.scene.overview_camera.rotation[0] += dy
                            self.scene.overview_camera.rotation[1] += dx
                        else:
                            self.scene.camera.rotation[0] += dy
                            self.scene.camera.rotation[1] += dx
                    self.last_pos = (x, y)
