class OrderRulesMethod:
    """
    Classe che rappresenta il criterio di ordinamento adottato
    per poter inserire le regole all'interno del conflict set.
    Ogni criterio d'ordinamento che si vorrà implementare dovrà
    estendere tale classe per poter rispettare la sua interfaccia
    """
    SALIENCE = 1
    RANDOM = 2
    DEPTH = 3

    def __init__(self):
        pass
    def add(self, rules, rule):
        pass

class RandomAdder(OrderRulesMethod):
    """
    Classe che rappresenta che organizza in
    maniera casuale le regole all'interno del conflict set.
    """
    def __init__(self):
        super().__init__()

    def add(self, rules, rule):
        rules.append(rule)

class DepthAdder(OrderRulesMethod):
    def __init__(self):
        super().__init__()

    def add(self, rules, rule):
        pass

class SalienceAdder(OrderRulesMethod):
    """
    Classe che rappresenta un criterio di ordinamento
    secondo il quale ogni regola viene inserita all'interno del
    conflict set facendo uso della priorità ad essa associata
    """
    def __init__(self):
        super().__init__()

    def add(self, rules, rule):
        pass
