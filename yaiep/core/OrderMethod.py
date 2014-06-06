

# #
# Classe che rappresenta il criterio di ordinamento adottato
# per poter inserire le regole all'interno del conflict set.
# Ogni criterio d'ordinamento che si vorrà implementare dovrà
# estendere tale classe per poter rispettare la sua interfaccia
#
class OrderRulesMethod:
    SALIENCE = 1
    RANDOM = 2
    DEPTH = 3

    def __init__(self):
        pass

    # #
    # Aggiunge al conflict set la regola specificata
    # secondo un preciso criterio di ordinamento
    #
    # @param rules conflict set nel quale verrà aggiunta la regola
    # @param rule regola da aggiungere
    def add(self, rules, rule):
        pass


# #
# Classe che rappresenta che organizza in
# maniera casuale le regole all'interno del conflict set.
#
class RandomAdder(OrderRulesMethod):
    def __init__(self):
        super().__init__()

    def add(self, rules, rule):
        rules.append(rule)


class DepthAdder(OrderRulesMethod):
    def __init__(self):
        super().__init__()

    def add(self, rules, rule):
        pass


# #
# Classe che rappresenta un criterio di ordinamento
# secondo il quale ogni regola viene inserita all'interno del
# conflict set facendo uso della priorità ad essa associata
#
class SalienceAdder(OrderRulesMethod):
    def __init__(self):
        super().__init__()

    def add(self, rules, rule):
        x = rule[0] if isinstance(rule, tuple) else rule
        lo = 0
        hi = len(rules)
        while lo < hi:
            mid = (lo+hi)//2
            if isinstance(rules[mid], tuple):
                if rules[mid][0] > x:
                    lo = mid+1
                else:
                    hi = mid
            else:
                if rules[mid] > x:
                    lo = mid+1
                else:
                    hi = mid

        rules.insert(lo, rule)