import pygame
from pygame.locals import KMOD_CTRL, KMOD_SHIFT, KMOD_ALT, K_r, K_t, K_c, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_o, K_p, K_DELETE
from OpenGL.GL import *

class EventListener:
    def __init__(self, scene):
        self.scene = scene
        self.last_pos = None
        self.rotate_mode = False
        self.translate_mode = False
        self.shear_mode = False
        self.overview_active = False 
    
    def run(self):
        mods = pygame.key.get_mods()
        ctrl_pressed = mods & KMOD_CTRL
        shift_pressed = mods & KMOD_SHIFT
        alt_pressed = mods & KMOD_ALT

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            elif event.type == pygame.KEYUP:
                self.handle_keyup(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event, ctrl_pressed, shift_pressed, alt_pressed)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event)
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mousemotion(event)

    def handle_keydown(self, event):
        if event.key == K_r:
            self.rotate_mode = True
        elif event.key == K_t:
            self.translate_mode = True
        # elif event.key == K_c:
        #     self.shear_mode = True
        elif event.key in [K_F1, K_F2, K_F3, K_F4, K_F5, K_F6]:
            self.set_preset_position(event.key)
        elif event.key == K_o:
            self.scene.show_overview = not self.scene.show_overview
            self.overview_active = self.scene.show_overview
        elif event.key == K_p:  # Tecla 'P' para alternar a visibilidade da Sidebar
            self.scene.sidebar.toggle_visibility()
        elif event.key == K_DELETE:
            self.delete_selected_object()

    def delete_selected_object(self):
        self.scene.delete_selected_object()

    def handle_keyup(self, event):
        if event.key == K_r:
            self.rotate_mode = False
        elif event.key == K_t:
            self.translate_mode = False
        elif event.key == K_c:
            self.shear_mode = False

    def handle_mousebuttondown(self, event, ctrl_pressed, shift_pressed, alt_pressed):
        x, y = pygame.mouse.get_pos()
        
        if event.button == 1:  # Botão esquerdo do mouse
            action = self.scene.sidebar.check_click(x, y, self.scene)
            if action:
                self.scene.message_queue.put(action)
            else:
                self.select_object(event, shift_pressed)
        elif event.button == 3:  # Botão direito do mouse
            self.last_pos = pygame.mouse.get_pos()
        elif event.button in [4, 5]:  # Scroll do mouse
            self.handle_scroll(event, ctrl_pressed, shift_pressed, alt_pressed)

    def handle_mousebuttonup(self, event):
        if event.button in [1, 3]:
            self.last_pos = None

    def handle_mousemotion(self, event):
        x, y = pygame.mouse.get_pos()
        self.scene.sidebar.update_hover(x, y)
        if self.last_pos:
            self.update_camera_position(event)

    def set_preset_position(self, key):
        preset_index = key - K_F1 + 1
        if self.scene.show_overview:
            self.scene.overview_camera.set_preset_position(preset_index)
        else:
            self.scene.camera.set_preset_position(preset_index)

    def select_object(self, event, shift_pressed):
        x, y = pygame.mouse.get_pos()
        hits = self.scene.select_object(x, y)
        if hits is not None and len(hits) > 0:
            selected_object_index = hits[3] - 1
            selected_object = self.scene.objects[selected_object_index]
            selected_object.selected = not selected_object.selected
            if selected_object.selected and not shift_pressed:
                for obj in self.scene.objects:
                    if obj != selected_object:
                        obj.selected = False
        self.last_pos = pygame.mouse.get_pos()

    def handle_scroll(self, event, ctrl_pressed, shift_pressed, alt_pressed):
        direction = 1 if event.button == 4 else -1
        value_rotate = 5 * direction
        value_translate = 0.1 * direction
        value_scale = 0.05 * direction
        min_scale = 0.05

        if any(obj.selected for obj in self.scene.objects):
            for obj in self.scene.objects:
                if obj.selected:
                    self.apply_transformations(obj, value_rotate, value_translate, value_scale, min_scale, ctrl_pressed, shift_pressed, alt_pressed)
        else:
            self.scene.camera.zoom += 0.5 * direction

    def apply_transformations(self, obj, value_rotate, value_translate, value_scale, min_scale, ctrl_pressed, shift_pressed, alt_pressed):
        if self.shear_mode and ctrl_pressed:
            obj.shear(value_scale, 'xy')
        elif ctrl_pressed:
            if self.rotate_mode:
                obj.rotate(value_rotate, (1, 0, 0))
            elif self.translate_mode:
                obj.translate(value_translate, (1, 0, 0))
            else:
                self.apply_scale(obj, value_scale, min_scale, (1, 0, 0))
        if shift_pressed:
            if self.rotate_mode:
                obj.rotate(value_rotate, (0, 1, 0))
            elif self.translate_mode:
                obj.translate(value_translate, (0, 1, 0))
            else:
                self.apply_scale(obj, value_scale, min_scale, (0, 1, 0))
        if alt_pressed:
            if self.rotate_mode:
                obj.rotate(value_rotate, (0, 0, 1))
            elif self.translate_mode:
                obj.translate(value_translate, (0, 0, 1))
            else:
                self.apply_scale(obj, value_scale, min_scale, (0, 0, 1))

    def apply_scale(self, obj, value_scale, min_scale, axis):
        current_scale = obj.transform.scale
        new_scale = [current_scale[i] + value_scale * axis[i] for i in range(3)]
        new_scale = [max(min_scale, s) for s in new_scale]
        obj.scale(new_scale[0] - current_scale[0], (1, 0, 0))
        obj.scale(new_scale[1] - current_scale[1], (0, 1, 0))
        obj.scale(new_scale[2] - current_scale[2], (0, 0, 1))

    def update_camera_position(self, event):
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
