from objects import Object
from OBJFileLoader import OBJ


class Mesh(Object):
    def __init__(self, position, filename, swapyz=False, default_mtl: tuple[str, str]=None):
        super().__init__(position)
        self.model = OBJ(filename, swapyz, default_mtl=('objects/mesh/default.mtl', 'Material'))
    
    def draw(self):
        self.model.render()
