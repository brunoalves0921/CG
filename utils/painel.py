import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

class Panel(QWidget):
    def __init__(self, message_queue):
        super().__init__()
        self.message_queue = message_queue
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.cube_button = QPushButton('Add Cube', self)
        self.cube_button.clicked.connect(lambda: self.add_object('cube'))
        layout.addWidget(self.cube_button)

        self.sphere_button = QPushButton('Add Sphere', self)
        self.sphere_button.clicked.connect(lambda: self.add_object('sphere'))
        layout.addWidget(self.sphere_button)

        self.cone_button = QPushButton('Add Cone', self)
        self.cone_button.clicked.connect(lambda: self.add_object('cone'))
        layout.addWidget(self.cone_button)

        self.cylinder_button = QPushButton('Add Cylinder', self)
        self.cylinder_button.clicked.connect(lambda: self.add_object('cylinder'))
        layout.addWidget(self.cylinder_button)

        self.halfsphere_button = QPushButton('Add Half Sphere', self)
        self.halfsphere_button.clicked.connect(lambda: self.add_object('halfsphere'))
        layout.addWidget(self.halfsphere_button)

        self.pyramid_button = QPushButton('Add Pyramid', self)
        self.pyramid_button.clicked.connect(lambda: self.add_object('pyramid'))
        layout.addWidget(self.pyramid_button)

        self.setLayout(layout)
        self.setWindowTitle('Object Panel')
        self.show()

    def add_object(self, object_type):
        self.message_queue.put(object_type)

def run_panel(message_queue):
    app = QApplication(sys.argv)
    panel = Panel(message_queue)
    sys.exit(app.exec_())
