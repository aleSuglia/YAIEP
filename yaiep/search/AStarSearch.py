## Modulo che presenta l'implementazione dell'algoritmo di ricerca informata A*

import bisect
from yaiep.graph.InfoNode import InfoNode
from yaiep.search.SearchMethod import SearchMethod


##
# Classe rappresentante l'algoritmo di ricerca informata A*
#
class AStarSearch(SearchMethod):

    ##
    # Costruttore della classe, genera il metodo di ricerca inizializzando i parametri in input
    #
    # @param graph: il grafo che verrà popolato dal metodo di ricerca
    # @param agenda: adoperata dal metodo di ricerca per gestire le regole attivabili
    # @param final_state: stato finale del processo solutivo
    # @param graphic_func: funzione necessaria per poter formattare le fasi di risoluzione del problema
    # @param heuristic: funzione euristica che verrà adottata per valutare la "bontà" di un nodo
    #
    def __init__(self, graph, agenda, final_state, graph_function, heuristic):
        SearchMethod.__init__(self, graph, agenda, final_state, graph_function)
        self._heuristic = heuristic

    ##
    # Genera tutti i nodi "vicini" al nodo in input
    # @param best_node: nodo di cui si vuole costruire la sua lista dei vicini
    # @param engine: motore inferenziale nella quale sono presenti tutte le informazioni necessarie
    # alla generazione dei vicini
    #
    #@return lista dei nodi vicini
    #
    def neighbor_nodes(self, best_node, engine):
        neighbors = []

        applicable_rules = self._agenda.get_activable_rules(best_node.wm)
        for rule in applicable_rules:
            new_node_wm = best_node.wm.copy()
            engine.apply_action(new_node_wm, rule)
            self._agenda.set_activated_rule(rule[0] if isinstance(rule, tuple) else rule)
            if engine.modify_working_mem(rule):
                self._agenda.restore_rules(new_node_wm)  # reinserire regole già attivate nella lista di regole non attivate
            new_node = InfoNode(new_node_wm, None)
            if not new_node in [x[0] for x in neighbors]:
                neighbors.append((new_node, rule))

        return neighbors

    ##
    # Aggiorna il gn di ogni nodo, in questo caso rappresenta la profondità in cui il nodo si trova
    # @param node: nodo nel quale si vuole aggiornare gn
    # @param curr_gn: profondità raggiunta nella costruzione del grafo
    #
    def update_gn_depth(self, node, curr_gn):
        sons = self._graph.neighbors(node)
        if not sons:
            node.gn = curr_gn
        else:
            for son in sons:
                if son.gn < curr_gn:
                    son.gn = curr_gn + 1
                    self.update_gn_depth(son, son.gn)

    ##
    # Esegue una A* search per poter ritrovare lo stato
    # che rappresenta lo stato finale del problema da risolvere.
    # La ricerca ha ugualmente fine nel momento in cui non vi sono più regole da attivare.
    #
    # @param engine: motore di inferenza che viene adoperato per poter condurre la ricerca
    #
    # @return True se è stata trovata almeno una soluzione, False altrimenti
    def execute(self, engine):
        opened_set = []
        closed_set = []

        root_node = InfoNode(self._graph.get_init_state().wm, None)

        # inizializzo i valori h(n) e g(n) del nodo radice
        root_node.gn = 0
        root_node.hn = self._heuristic(root_node.wm) if self._heuristic else 0
        already_in_open = False
        already_in_closed = False

        #opened_set.append(root_node) # aggiungo il nodo radice come primo elemento da esplorare
        bisect.insort(opened_set, root_node)

        while opened_set:
            best_node = opened_set.pop(0)
            if not best_node in closed_set:
                closed_set.append(best_node)

            #if best_node.wm.match_fact(self._final_state):
            if self.match_final_state(best_node):
                # ho raggiunto l'obiettivo SUCCESSO
                self._solution.append(best_node)
                self.costruct_path_to_solution()
            else:
                best_node_neighbors = self.neighbor_nodes(best_node, engine)

                # per ogni suo figlio, crea un arco che va dal figlio al padre
                for i in range(len(best_node_neighbors)):
                    son = best_node_neighbors[i][0]
                    rule_tuple = best_node_neighbors[i][1]
                    son.parent = best_node
                    son.gn = best_node.gn + 1

                    old_node = None
                    for old in opened_set:
                        if son == old:
                            old_node = old
                            already_in_open = True
                            break

                    # il nodo corrente è già presente in opened
                    if old_node:
                        # old_node più conveniente di son
                        if old_node.gn < son.gn:
                            son.gn = old_node.gn
                            son.parent = old_node.parent
                    else: # il nodo corrente non è presente in opened
                        # vedi se il nodo è in closed!!
                        closed_old_node = None
                        for old in closed_set:
                            if son == old:
                                closed_old_node = old
                                already_in_closed = True
                                break
                        if closed_old_node: # nodo corrente in closed_set
                            # closed_old_node più conveniente di son
                            if closed_old_node.gn < son.gn:
                                son.gn = closed_old_node.gn
                                son.parent = closed_old_node.parent
                            else:  # son più conveniente di closed_old_node
                                self.update_gn_depth(closed_old_node, son.gn)

                    #if not son in opened_set and not son in closed_set:
                    if not already_in_open and not already_in_closed:
                        son.hn = self._heuristic(son.wm) if self._heuristic else 0
                        bisect.insort(opened_set, son)
                        self._graph.add_edge(best_node, son, {'rule': rule_tuple[0] if isinstance(rule_tuple, tuple) else rule_tuple})

                    already_in_closed = already_in_open = False
        return len(self._solution) > 0

    ##
    # Esegue una A* search poter ritrovare lo stato
    # che rappresenta lo stato finale del problema da risolvere.
    # La ricerca ha fine nel momento in cui ha trovato la prima soluzione disponibile con i parametri in input
    # oppure non vi sono più regole da attivare.
    #
    # @param engine: motore di inferenza che viene adoperato per poter condurre la ricerca
    # @param opened_nodes: insieme dei nodi non ancora esplorati
    # @param closed_nodes: insieme dei nodi esplorati
    #
    # @return True se è stata trovata almeno una soluzione, False altrimenti
    def step_execute(self, engine, opened_set, closed_set):
        if not opened_set and not closed_set:
            root_node = InfoNode(self._graph.get_init_state().wm, None)

            # inizializzo i valori h(n) e g(n) del nodo radice
            root_node.gn = 0
            root_node.hn = self._heuristic(root_node.wm) if self._heuristic else 0

            opened_set.append(root_node) # aggiungo il nodo radice come primo elemento da esplorare

        already_in_open = False
        already_in_closed = False

        while opened_set:
            best_node = opened_set.pop(0)
            if not best_node in closed_set:
                closed_set.append(best_node)

            #if best_node.wm.match_fact(self._final_state):
            if self.match_final_state(best_node):
                # ho raggiunto l'obiettivo SUCCESSO
                self._solution.append(best_node)
                self.costruct_path_to_solution()
                return True
            else:
                best_node_neighbors = self.neighbor_nodes(best_node, engine)

                # per ogni suo figlio, crea un arco che va dal figlio al padre
                for i in range(len(best_node_neighbors)):
                    son = best_node_neighbors[i][0]
                    rule_tuple = best_node_neighbors[i][1]
                    son.parent = best_node
                    son.gn = best_node.gn + 1

                    old_node = None
                    for old in opened_set:
                        if son == old:
                            old_node = old
                            already_in_open = True
                            break

                    # il nodo corrente è già presente in opened
                    if old_node:
                        # old_node più conveniente di son
                        if old_node.gn < son.gn:
                            son.gn = old_node.gn
                            son.parent = old_node.parent
                    else: # il nodo corrente non è presente in opened
                        # vedi se il nodo è in closed!!
                        closed_old_node = None
                        for old in closed_set:
                            if son == old:
                                closed_old_node = old
                                already_in_closed = True
                                break
                        if closed_old_node: # nodo corrente in closed_set
                            # closed_old_node più conveniente di son
                            if closed_old_node.gn < son.gn:
                                son.gn = closed_old_node.gn
                                son.parent = closed_old_node.parent
                            else:  # son più conveniente di closed_old_node
                                self.update_gn_depth(closed_old_node, son.gn)

                    #if not son in opened_set and not son in closed_set:
                    if not already_in_open and not already_in_closed:
                        son.hn = self._heuristic(son.wm) if self._heuristic else 0
                        bisect.insort(opened_set, son)
                        self._graph.add_edge(best_node, son, {'rule': rule_tuple[0] if isinstance(rule_tuple, tuple) else rule_tuple})

                    already_in_closed = already_in_open = False

        return len(self._solution) > 0
