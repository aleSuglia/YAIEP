class OrderRulesMethod:
    SALIENCE = 1
    RANDOM = 2
    DEPTH = 3

    def __init__(self):
        pass
    def add(self, rules, rule):
        pass

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

class SalienceAdder(OrderRulesMethod):
    def __init__(self):
        super().__init__()

    def add(self, rules, rule):
        pass
