from pyparsing import Literal, Word, OneOrMore, alphas, Group, QuotedString
from yaiep.core.Rule import Rule


class C5RuleParser:
    """
    Classe che rappresenta un parser per il file che contiene le regole che verrà adoperato
    dal tool di generazione degli alberi di decisione
    """
    _rule_line = OneOrMore(Group(Word(alphas) + Literal('=').suppress() + QuotedString('"')))
    _rule_file = OneOrMore(_rule_line)
    def __init__(self):
        """
        Inizializza gli elementi che la classe adopererà per poter avviare il processo
        di parsing delle regole
        """
        self._rule_list = {}
        self._class_name = None

    def _read_class_name(self, filename):
        """
        Acquisisce il nome dell'attributo di classe del dataset corrente
        @param filename: nome del file contenente i nomi degli attributi del dataset
        """
        with open(filename) as names_file:
            first_line = names_file.readline()
            self._class_name = first_line[:first_line.index(".")]

    def getRules(self, rule_filename, names_file):

        """
            @param rule_filename file contenente le regole
            @param names_file file contenente il nome dell'attributo di classe (prima linea)
        """

        curr_rule = None
        curr_conditions = []
        self._read_class_name(names_file)

        with open(rule_filename) as rule_file:
            for line in rule_file:
                parsed_line = C5RuleParser._rule_line.parseString(line).asList()

                if 'conds' in parsed_line[0]:
                    if curr_rule is None: # first rule found
                        curr_rule = Rule()
                    else:
                        curr_rule.conditions = curr_conditions[:]
                        curr_conditions.clear()
                        #self._rule_list.append(curr_rule)
                        self._rule_list[curr_rule] = curr_rule.actions
                        curr_rule = Rule()

                    curr_rule.conditions = curr_conditions
                    curr_rule.actions = ['assert', [self._class_name, parsed_line[4][1]]]

                elif 'type' in parsed_line[0]:
                    curr_conditions.append([parsed_line[1][1], parsed_line[2][1]])

        return self._rule_list


