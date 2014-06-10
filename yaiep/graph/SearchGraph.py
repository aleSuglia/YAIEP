import networkx
from yaiep.graph.Node import Node


##
# Classe che rappresenta l'intero spazio di ricerca che viene
# generato via via che il metodo di ricerca ispeziona nuovi nodi
#
class SearchGraph(networkx.DiGraph):
    ##
    # Crea il grafo di ricerca come un grafo direzionato
    # il quale ha come nodo iniziale lo stato iniziale
    # dal quale il metodo di ricerca partirà per poter esplorare
    # lo spazio delle soluzioni
    #
    # @param init_state stato iniziale dal quale inizia la ricerca
    def __init__(self, init_state):
        networkx.DiGraph.__init__(self)
        self._init_state = Node(init_state.copy(), None)
        # inserisci lo stato iniziale a partire dal quale ispezionare lo spazio di ricerca
        self.add_node(self._init_state)

    ##
    # Restituisce il riferimento allo stato iniziale dal
    # quale è iniziata la ricerca
    #
    def get_init_state(self):
        return self._init_state

    def __str__(self):
        res = ''

        for node in self:
            res += '{0} -> '.format(str(node.wm))
            for adj in self.neighbors(node):
                res += str(adj.wm) + '\n'

        return res

