from yaiep.graph.Node import Node


# #
# Classe che rappresenta un nodo adoperato da un metodo
# di ricerca informato
# Rappresenta una sotto classe della classe Nodo, la quale
# presenta delle informazioni utili al metodo informato quali
# il valore che rappresenta il numero di passi necessari per poter raggiungere
# il nodo corrente dalla radice (gn) e il numero di passi (stimato) per poter
# raggiungere il goal dal nodo corrente
class InfoNode(Node):
    def __init__(self, wm, parent):
        Node.__init__(self, wm, parent)
        self.hn = 0
        self.gn = 0

    def __hash__(self):
        return hash(self.wm)

    def __eq__(self, other):
        return self.wm == other.wm

    def __lt__(self, other):
        return (self.gn + self.hn) > (other.gn + other.hn)

    def __gt__(self, other):
        return (self.gn + self.hn) < (other.gn + other.hn)

    def __le__(self, other):
        return (self.gn + self.hn) >= (other.gn + other.hn) and self == other

    def __ge__(self, other):
        return (self.gn + self.hn) <= (other.gn + other.hn) and self == other

    def __ne__(self, other):
        return not self == other

