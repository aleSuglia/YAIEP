from yaiep.graph.InfoNode import InfoNode
from yaiep.search.SearchMethod import SearchMethod


'''
    function A*(start,goal)
    closedset := the empty set    // The set of nodes already evaluated.
    openset := {start}    // The set of tentative nodes to be evaluated, initially containing the start node
    came_from := the empty map    // The map of navigated nodes.

    g_score[start] := 0    // Cost from start along best known path.
    // Estimated total cost from start to goal through y.
    f_score[start] := g_score[start] + heuristic_cost_estimate(start, goal)

    while openset is not empty
        current := the node in openset having the lowest f_score[] value
        if current = goal
            return reconstruct_path(came_from, goal)

        remove current from openset
        add current to closedset
        for each neighbor in neighbor_nodes(current)
            if neighbor in closedset
                continue
            tentative_g_score := g_score[current] + dist_between(current,neighbor)

            if neighbor not in openset or tentative_g_score < g_score[neighbor]
                came_from[neighbor] := current
                g_score[neighbor] := tentative_g_score
                f_score[neighbor] := g_score[neighbor] + heuristic_cost_estimate(neighbor, goal)
                if neighbor not in openset
                    add neighbor to openset

    return failure
'''

class AStarSearch(SearchMethod):
    def __init__(self, graph, agenda, final_state, heuristic, all_solutions=False):
        SearchMethod.__init__(self, graph, agenda, final_state, all_solutions)
        self._heuristic = heuristic

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
            neighbors.append((new_node, rule))

        return neighbors

    def execute(self, engine):

        opened_set = set()
        closed_set = []

        root_node = InfoNode(self._graph.get_init_state().wm, None)

        # inizializzo i valori h(n) e g(n) del nodo radice
        root_node.gn = 0
        root_node.hn = self._heuristic(root_node.wm)

        opened_set.add(root_node) # aggiungo il nodo radice come primo elemento da esplorare

        while opened_set:
            best_node = opened_set.pop()
            if best_node.wm.match_fact(self._final_state):
                return True # ho raggiunto l'obiettivo SUCCESSO

            closed_set.append(best_node)

            best_node_neighbors = self.neighbor_nodes(best_node, engine)
            for neighbor_pair in best_node_neighbors:
                neighbor = neighbor_pair[0]
                neighbor_rule = neighbor_pair[1]
                if neighbor in closed_set:
                    continue

                tentative_g_score = best_node.gn + 1

                if neighbor not in opened_set or tentative_g_score < neighbor.gn:
                    neighbor.parent = best_node
                    self._graph.add_edge(best_node, neighbor, {'rule':neighbor_rule})
                    neighbor.gn = tentative_g_score
                    neighbor.hn = self._heuristic(neighbor.wm)
                    if neighbor not in opened_set:
                        opened_set.add(neighbor)

        return False


