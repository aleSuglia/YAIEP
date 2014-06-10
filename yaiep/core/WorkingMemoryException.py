

##
# Classe che rappresenta una condizionale eccezionale
# che può verificarsi all'interno della Working Memory
#
class WorkingMemoryException(Exception):
    def_msg = 'WM Exception'

    def __init__(self, value=def_msg):
        self.value = value

    def __repr__(self):
        return "WM Exception: " + repr(self.value)