import networkx
from yaiep.core.UIManager import UIManager


##
# Classe che rappresenta la struttura di base di un metodo di ricerca adoperato
# dal motore di inferenza per ispezionare lo spazio delle possibili soluzioni.
#
class SearchMethod:
    ##
    # Inizializza un metodo di ricerca inizializzando tutti i suoi componenti
    # principali
    # @param graph: il grafo che verrà popolato dal metodo di ricerca
    # @param agenda: adoperata dal metodo di ricerca per gestire le regole attivabili
    # @param final_state: stato finale del processo solutivo
    # @param graphic_func: funzione necessaria per poter formattare le fasi di risoluzione del problema
    #
    def __init__(self, graph, agenda, final_state, graphic_func):
        self._graph = graph
        self._agenda = agenda
        self._final_state = final_state
        self._solution = []
        self._path_solution = []
        self._graphic_func = graphic_func

    ##
    # Avvia la risoluzione del problema sfruttando il motore di inferenza passato come parametro.
    # ATTENZIONE: tale metodo deve essere implementato da una opportuna sottoclasse
    # @param engine: il motore di inferenza che adopera il metodo di ricerca.
    # @return: True se è stata trovato una soluzione(o soluzioni), False altrimenti
    #
    def execute(self, engine):
        pass

    def step_execute(self, engine, opened_nodes, closed_nodes):
        pass

    ##
    # Ricostruisce il percorso per poter raggiungere la soluzione a partire dallo stato iniziale.
    #
    def costruct_path_to_solution(self):
        if not self._solution is None:
            curr_path = networkx.DiGraph()
            curr_node = self._solution[-1]
            while curr_node != self._graph.get_init_state():
                data = self._graph.get_edge_data(curr_node.parent, curr_node)
                curr_path.add_edge(curr_node.parent, curr_node, data)
                curr_node = curr_node.parent

            self._path_solution.append(curr_path)

    ##
    # Restituisce il percorso necessario per poter raggiungere la soluzione sotto forma di un grafo, avente
    # come nodi una serie di Working memory e come archi le regole che permettono di transitare da uno stato
    # ad un altro
    # @return: il percorso solutivo trovato dal metodo di ricerca
    #
    def get_path_to_solution(self):
        return self._path_solution

    ##
    # Restituisce la soluzione al problema risolto dal metodo di ricerca ed eventualmente
    # il percorso necessario per poterla raggiungere.
    #
    # E' opportuno controllare la validità della tupla in quanto potrebbe non essere presente alcuna soluzione.
    # @return: una tupla che ha come primo elemento la soluzione ottenuta e come secondo elemento il percorso
    #
    def get_solution(self):
        return self._solution, self._path_solution

    ##
    # Stampa a video tutte le soluzioni del problema trovate dall'algoritmo di ricerca
    #
    def print_solution_path(self):

        continue_search_flag = True
        i = 0
        tot_num_solutions = len(self._solution)

        while continue_search_flag and i < tot_num_solutions:
            curr_node = self._graph.get_init_state()
            path = self._path_solution[i]
            solution = self._solution[i]

            print("Solution #{0}".format(i+1))
            if not curr_node is None:
                cont_rule = 1

                while curr_node != solution:
                    son = path.neighbors(curr_node)[0]
                    if self._graphic_func:
                        self._graphic_func(curr_node.wm)
                    else:
                        print('{0} - {1}'.format(cont_rule, path.get_edge_data(curr_node, son)['rule']))

                    cont_rule += 1
                    curr_node = son

                if self._graphic_func:
                    self._graphic_func(curr_node.wm)

                i += 1
                continue_search_flag = UIManager.continue_search()

        if continue_search_flag and i == tot_num_solutions:
            print("No more solutions found")

    ##
    # Stampa a video il nodo corrente della soluzione che si stà analizzando nel caso in cui si
    # stata definita una funzione di graphics altrimenti la regola utilizzata per la generazione del nodo
    # @param curr_node: nodo appartenente alla soluzione di cui si vogliono visualizzare le informazioni
    # @param path_index: indice rappresentante la soluzione che si sta analizzando
    #
    def print_step_solution(self, curr_node, path_index):
        if not self._solution:
            print("No solution found!")
        elif curr_node and path_index < len(self._path_solution):
            path = self._path_solution[path_index]
            root_node = self._graph.get_init_state()
            is_root = curr_node == root_node.wm
            if is_root:
                curr_node = root_node

            if curr_node != self._solution[path_index]:
                son = path.neighbors(curr_node)[0]
                if self._graphic_func:
                    self._graphic_func(curr_node.wm)
                else:
                    print('{1}'.format(path.get_edge_data(curr_node, son)['rule']))
                return son  # il nuovo nodo di riferimento diviene il figlio
            else:
                if self._graphic_func:
                    self._graphic_func(curr_node.wm)

                return None

    ##
    # Permette al metodo di ricerca di verificare se lo stato corrente
    # rappresenta uno stato finale per il problema.
    #
    # @param curr_state lo stato corrente da verificare
    # @return True se lo stato corrente è uno stato finale False diversamente
    #
    def match_final_state(self, curr_state):
        # se non è stato definito uno stato finale
        if not self._final_state:
            return False

        all_matched = True

        for final_state in self._final_state:
            # lo stato finale prevede delle variabili
            if final_state.has_variable():
                curr_fact_list = curr_state.wm.get_fact_list()
                final_state_attributes = final_state.get_attributes()
                len_final_state_attributes = len(final_state_attributes)

                matched_fact = False

                for fact in curr_fact_list.values():
                    if fact.get_name() == final_state.get_name():
                        curr_attributes = fact.get_attributes()
                        if len(curr_attributes) == len_final_state_attributes:
                            # i fatti in esame sono dei template
                            if fact.is_template() and final_state.is_template():
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
                            elif not fact.is_template() and not final_state.is_template():
                                i = 0
                                while i < len_final_state_attributes:
                                    if final_state_attributes[i].startswith('?'):
                                        pass
                                    else:
                                        if final_state_attributes[i] != curr_attributes[i]:
                                            break
                                    i += 1
                                matched_fact = True if i == len_final_state_attributes else False

                all_matched = all_matched and matched_fact
            else:
                # effettua un match canonico con lo stato finale
                all_matched = all_matched and not curr_state.wm.match_fact(final_state) is None

        return all_matched