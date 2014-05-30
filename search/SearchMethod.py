import networkx


class SearchMethod:
    """
    Rappresenta la struttura di base di un metodo di ricerca adoperato
    dal motore di inferenza per ispezionare lo spazio delle possibili soluzioni.

    """

    def __init__(self, graph, agenda, final_state, all_solutions=False):
        """
        Istanzia un metodo di ricerca inizializzando tutti i suoi componenti
        principali
        @param graph: il grafo che verrà popolato dal metodo di ricerca
        @param agenda: adoperata dal metodo di ricerca per gestire le regole attivabili
        @param final_state: stato finale del processo solutivo
        @param all_solutions: indica se il processo di ricerca dovrà restituire tutte le possibili soluzioni (default: false)
        """
        self._graph = graph
        self._agenda = agenda
        self._final_state = final_state
        self._all_solutions = all_solutions
        self._solution = []
        self._path_solution = []

    def execute(self, engine):
        """
        Avvia la risoluzione del problema sfruttando il motore di inferenza passato come parametro.
        ATTENZIONE: tale metodo deve essere implementato da una opportuna sottoclasse
        @param engine: il motore di inferenza che adopera il metodo di ricerca.
        @return: True se è stata trovato una soluzione(o soluzioni), False altrimenti
        """
        pass

    def costruct_path_to_solution(self):
        """
        Ricostruisce il percorso per poter raggiungere la soluzione a partire dallo stato iniziale.
        """
        if not self._solution is None:
            curr_path = networkx.DiGraph()
            curr_node = self._solution[-1]
            while curr_node != self._graph.get_init_state():
                data = self._graph.get_edge_data(curr_node.parent, curr_node)
                curr_path.add_edge(curr_node.parent, curr_node, data)
                curr_node = curr_node.parent

            self._path_solution.append(curr_path)


    def get_path_to_solution(self):
        """
        Restituisce il percorso necessario per poter raggiungere la soluzione sotto forma di un grafo, avente
        come nodi una serie di Working memory e come archi le regole che permettono di transitare da uno stato
        ad un altro
        @return: il percorso solutivo trovato dal metodo di ricerca
        """
        return self._path_solution

    def get_solution(self):
        """
        Restituisce la soluzione al problema risolto dal metodo di ricerca ed eventualmente
        il percorso necessario per poterla raggiungere.

        E' opportuno controllare la validità della tupla in quanto potrebbe non essere presente alcuna soluzione.
        @return: una tupla che ha come primo elemento la soluzione ottenuta e come secondo elemento il percorso
        """
        return self._solution, self._path_solution

    def continue_search(self):
        value = input('Are you satisfied with this solution? (y/n): ')
        if value == 'n':
            return True
        else:
            return False

    def print_solution_path(self):
        curr_node = self._graph.get_init_state()
        path = self._path_solution[-1]  # sceglie l'ultimo percorso generato
        solution = self._solution[-1]  # sceglie l'ultima soluzione trovata

        if not curr_node is None:
            cont_rule = 1
            while curr_node != solution:
                son = path.neighbors(curr_node)[0]
                print('{0} - {1}'.format(cont_rule, path.get_edge_data(curr_node, son)['rule']))
                cont_rule += 1
                curr_node = son

    def match_final_state(self, curr_state):
        '''
        Permette al metodo di ricerca di verificare se lo stato corrente
        rappresenta uno stato finale per il problema.

        @param curr_state lo stato corrente da verificare
        @return True se lo stato corrente è uno stato finale False diversamente
        '''
        # se non è stato definito uno stato finale
        if self._final_state.get_attributes() is None:
            return False

        # lo stato finale prevede delle variabili
        if self._final_state.has_variable():
            curr_fact_list = curr_state.wm.get_fact_list()
            final_state_attributes = self._final_state.get_attributes()
            len_final_state_attributes = len(final_state_attributes)

            matched_fact = False

            for fact in curr_fact_list.values():
                if fact.get_name() == self._final_state.get_name():
                    curr_attributes = fact.get_attributes()
                    if len(curr_attributes) == len_final_state_attributes:
                        # i fatti in esame sono dei template
                        if fact.is_template() and self._final_state.is_template():
                            i = 0
                            while i < len_final_state_attributes:
                                if final_state_attributes[i][1].startswith('?'):
                                    pass
                                else:
                                    if final_state_attributes[i] != curr_attributes[i]:
                                        break
                                i += 1
                            matched_fact = True if i == len_final_state_attributes else False
                            # i fatti in esame sono dei semplici fatti
                        elif not fact.is_template() and not self._final_state.is_template():
                            i = 0
                            while i < len_final_state_attributes:
                                if final_state_attributes[i].startswith('?'):
                                    pass
                                else:
                                    if final_state_attributes[i] != curr_attributes[i]:
                                        break
                                i += 1
                            matched_fact = True if i == len_final_state_attributes else False

            return matched_fact

        else:
            # effettua un match canonico con lo stato finale
            return curr_state.wm.match_fact(self._final_state)
