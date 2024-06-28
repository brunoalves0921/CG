import queue
from utils.scene import Scene
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import atexit

def main():
    # Cria a fila de mensagens
    message_queue = queue.Queue()

    # Cria a cena
    scene = Scene(message_queue)

    # Carregar o estado do cenário ao iniciar
    scene.load_scene('scene_state.json')

    # Registrar a função de salvar o estado ao fechar
    atexit.register(scene.save_scene, 'scene_state.json')

    # Inicia o loop principal da cena
    scene.start_main_loop()

if __name__ == "__main__":
    main()
