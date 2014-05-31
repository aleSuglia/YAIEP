# #
# Classe che rappresenta la parte sinistra di una regola
# nella quale vi sono le condizioni (sotto forma di fatti
# della WM o sotto forma di condizioni booleane semplici)
# che devono essere verificate per poter attivare le azioni
# associata alla regola
#
class LeftSideRule:
    # #
    # Inizializza la parte sinistra adoperando
    # la lista di condizioni specificata in input
    #
    def __init__(self, conditions):
        self.conditions = conditions
        self._string_form = ""
        self._init_string_form()

    def _init_string_form(self):
        for cond in self.conditions:
            self._string_form += str(cond) + " "

    def __hash__(self):
        return hash(self._string_form)

    def __str__(self):
        return self._string_form

    def __repr__(self):
        return self._string_form

    def __eq__(self, other):
        if isinstance(other, Rule):
            return False
        return self._string_form == str(other)


# #
# Classe che rappresenta la parte destra della regola
# nella quale vi sono le azioni che il motore deve eseguire
# in seguito al verificarsi delle condizioni presenti nella parte
# sinistra
#
class RightSideRule:
    # #
    # Provvede ad inizializzare la lista delle azioni
    # che dovranno essere innescate a seguito dell'attivazione
    # della regola prelevandole dalla lista di azioni specificata
    #
    #
    def __init__(self, actions):
        self.actions = actions
        self.string_form = ""
        self._init_string_form()

    def _init_string_form(self):
        for act in self.actions:
            self.string_form += str(act) + " "

    def __str__(self):
        return self.string_form

    def __repr__(self):
        return self.string_form


# #
# Classe composita che permette di rappresenta nella sua interezza
# una regola
#
class Rule:
    def __init__(self, conditions = None, actions = None):
        if conditions:
            self.conditions = LeftSideRule(conditions)
        else:
            self.conditions = []
        if actions:
            self.actions = RightSideRule(actions)
        else:
            self.conditions = []

    def __str__(self):
        return 'if ' + str(self.conditions) + ' then ' + str(self.actions)

    def __repr__(self):
        return str(self.conditions) + ' '

    def __eq__(self, other):
        if isinstance(other, Rule):
            return False
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))
