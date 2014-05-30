from yaiep.graph.Node import Node


class InfoNode(Node):
    def __init__(self, wm, parent):
        Node.__init__(self, wm, parent)
        self.hn = 0
        self.gn = 0

    def __eq__(self, other):
        return self.equals(other) and self.gn == other.gn

    def __lt__(self, other):
        return (self.gn + self.hn) < (other.gn + other.hn)

    def __gt__(self, other):
        return (self.gn + self.hn) > (other.gn + other.hn)

    def __le__(self, other):
        return (self.gn + self.hn) <= (other.gn + other.hn) and self.equals(other)

    def __ge__(self, other):
        return (self.gn + self.hn) >= (other.gn + other.hn) and self.equals(other)

    def __ne__(self, other):
        return (self.gn + self.hn) != (other.gn + other.hn) and not self.equals(other)

