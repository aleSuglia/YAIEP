# #
# Rappresenta la classe che contiene le informazioni di un nodo del
# che costituisce il grafo che compone lo spazio di ricerca.
#
class Node:
    ##
    # Inizializza il nodo corrente impostando la Working memory che rappresenta
    # e quale sia il suo nodo padre
    # @param wm: working memory contenuta nel nodo corrente
    # @param parent: nodo padre del nodo corrente
    #
    def __init__(self, wm, parent):
        self.parent = parent
        self.wm = wm

    ##
    # Provvede a verificare se due nodi sono uguali
    # @param other: Nodo con il quale effettuare il confronto
    # @return: True se i due nodi rappresentano la medesima WorkingMemory, False altrimenti
    #
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False

        return self.wm == other.wm

    def __hash__(self):
        return hash(self.wm)