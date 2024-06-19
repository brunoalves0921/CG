import queue
from utils.scene import Scene
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def main():
    # Cria a fila de mensagens
    message_queue = queue.Queue()

    # Cria a cena
    scene = Scene(message_queue)

    # Inicia o loop principal da cena
    scene.start_main_loop()

if __name__ == "__main__":
    main()
