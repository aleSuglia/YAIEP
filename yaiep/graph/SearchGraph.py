import networkx
from yaiep.graph.Node import Node
from yaiep.search.SearchMethod import SearchMethod


class SearchGraph(networkx.DiGraph):
    def __init__(self, init_state):
        networkx.DiGraph.__init__(self)
        self._init_state = Node(init_state.copy(), None)
        self.add_node(self._init_state) # inserisci lo stato iniziale a partire dal quale ispezionare lo spazio di ricerca


    def get_init_state(self):
        return self._init_state

    def __str__(self):
        res = ''

        for node in self:
            res += '{0} -> '.format(str(node.wm))
            for adj in self.neighbors(node):
                res += str(adj.wm) + '\n'

        return res

