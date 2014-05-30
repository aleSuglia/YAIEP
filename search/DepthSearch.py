from yaiep.graph.Node import Node
from yaiep.search.SearchMethod import SearchMethod


class DepthSearch(SearchMethod):
    def execute(self, engine):
        """
        Esegue una depth-first search (visita in profondità) per poter ritrovare lo stato
        che rappresenta lo stato finale del problema da risolvere.
        La ricerca ha ugualmente fine nel momento in cui non vi sono più regole da attivare.

        @param engine: motore di inferenza che viene adoperato per poter condurre la ricerca
        """
        root_node = self._graph.get_init_state()

        opened_nodes = [root_node]
        closed_nodes = []
        continue_search_flag = True
        num_solution = 1

        # finchè vi sono dei nodi da esplorare
        while opened_nodes and continue_search_flag:
            curr_node = opened_nodes.pop()
            if not curr_node in closed_nodes:
                closed_nodes.append(curr_node)

            # ho raggiunto l'obiettivo
            if self.match_final_state(curr_node):
                self._solution.append(curr_node) # salvo il nodo soluzione
                self.costruct_path_to_solution()
                print('Solution #{0}\n'.format(num_solution))
                self.print_solution_path()
                num_solution += 1
                continue_search_flag = self.continue_search()
            else:
                applicable_rules = self._agenda.get_activable_rules(curr_node.wm)
                for rule in applicable_rules:
                    new_node_wm = curr_node.wm.copy()
                    engine.apply_action(new_node_wm, rule)
                    self._agenda.set_activated_rule(rule[0] if isinstance(rule, tuple) else rule)
                    if engine.modify_working_mem(rule):
                        self._agenda.restore_rules(new_node_wm)  # reinserire regole già attivate nella lista di regole non attivate
                    new_node = Node(new_node_wm, curr_node)

                    # ispezione solo NUOVI nodi
                    if not new_node in closed_nodes and not new_node in opened_nodes:
                        self._graph.add_edge(curr_node, new_node, {'rule':rule[0] if isinstance(rule, tuple) else rule})
                        opened_nodes.append(new_node)


        if not opened_nodes and continue_search_flag:
            print('No more solution found.')
        return len(self._solution) > 0


