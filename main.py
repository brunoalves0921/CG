import threading
import queue
from utils.scene import Scene
from utils.painel import run_panel
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def main():
    # Cria a fila de mensagens
    message_queue = queue.Queue()

    # Cria a cena
    scene = Scene(message_queue)

    # Inicia o painel em uma thread separada
    panel_thread = threading.Thread(target=run_panel, args=(message_queue,))
    panel_thread.start()

    # Inicia o loop principal da cena
    scene.start_main_loop()

if __name__ == "__main__":
    main()
