from pyparsing import Literal, Word, OneOrMore, alphas, Group, QuotedString
from yaiep.core.Rule import Rule, LeftSideRule, RightSideRule


##
# Classe che rappresenta un parser per il file che contiene le regole che verrà adoperato
# dal tool di generazione degli alberi di decisione
#
class C5RuleParser:
    _rule_line = OneOrMore(Group(Word(alphas) + Literal('=').suppress() + QuotedString('"')))
    _rule_file = OneOrMore(_rule_line)

    ##
    # Inizializza gli elementi che la classe adopererà per poter avviare il processo
    # di parsing delle regole
    #
    def __init__(self):
        self._rule_list = []
        self._class_name = None

    ##
    # Acquisisce il nome dell'attributo di classe del dataset corrente
    # @param filename: nome del file contenente i nomi degli attributi del dataset
    def _read_class_name(self, filename):
        with open(filename) as names_file:
            first_line = names_file.readline()
            self._class_name = first_line[:first_line.index(".")]

    ##
    # Acquisisce le regole generate dal tool di machine learning e formattate secondo una specifica
    # sintassi
    # @param rule_filename file contenente le regole
    # @param names_file file contenente il nome dell'attributo di classe (prima linea)
    #
    def get_rules(self, rule_filename, names_file):
        curr_rule = None
        curr_conditions = []
        value_condition = []
        variables_index = 0
        self._read_class_name(names_file)

        with open(rule_filename) as rule_file:
            for line in rule_file:
                parsed_line = C5RuleParser._rule_line.parseString(line).asList()

                if 'conds' in parsed_line[0]:
                    if curr_rule is None: # first rule found
                        curr_rule = Rule()
                    else:
                        curr_conditions.extend(value_condition)
                        curr_rule.conditions = LeftSideRule(curr_conditions[:])
                        value_condition.clear()
                        curr_conditions.clear()
                        variables_index = 0
                        self._rule_list.append(curr_rule)
                        #self._rule_list[curr_rule] = curr_rule.actions
                        curr_rule = Rule()

                    curr_rule.conditions = LeftSideRule(curr_conditions)
                    curr_rule.actions = RightSideRule([['assert', [self._class_name, parsed_line[4][1]]]])

                elif 'type' in parsed_line[0]:
                    value_type = parsed_line[2][0]
                    if value_type != 'cut':
                        curr_conditions.append([parsed_line[1][1], parsed_line[2][1]])
                    else:
                        variable = '?' + parsed_line[1][1]
                        variables_index += 1
                        curr_conditions.append([parsed_line[1][1], variable])
                        value_condition.append('({0} {1} {2})'.format(variable, parsed_line[3][1], parsed_line[2][1]))


        return self._rule_list


