from pyparsing import ParseException
from yaiep.core.Fact import Fact
from yaiep.core.Rule import Rule
from yaiep.core.Slot import Slot
from yaiep.core.Template import Template
from yaiep.core.UIManager import UIManager
from yaiep.core.Utils import Utils
from yaiep.core.WorkingMemoryException import WorkingMemoryException
from yaiep.grammar.YAIEPGrammar import YAIEPGrammar

# #
# Classe che provvede al caricamento dal file di configurazione degli elementi necessari al motore
# di inferenza, tra le quali vi sono le regole, i fatti e i template.
#
class GrammarParser:
    ##
    # Effettua il parsing del file di configurazione a partire da quella che è la grammatica specifica del file
    # e provvedere ad avvalorare i parametri passati al metodo.
    # @param rules_filename: nome del file di configurazione
    # @param working_mem: oggetto istanza della classe WorkingMemory
    # @param list_rules: lista di regole
    # @param goal_state: oggetto istanza della classe Fact che rappresenta lo stato finale del problema
    # @param globals_vars: dizionario contenente le variabili globali definite nel file
    #
    @staticmethod
    def load_grammar(rules_filename, working_mem, list_rules, goal_state, globals_vars):
        grammar = YAIEPGrammar()
        parser = grammar.get_grammar_definition()
        GrammarParser._interpret_results(rules_filename, parser, working_mem, list_rules, grammar.get_keyword_list(),
                                         goal_state, globals_vars)

    ##
    # Permette di trasformare gli elementi presenti all'interno del file di configurazione, in oggetti
    # che verrano adoperati dal motore di inferenza per poter portare a termine i propri compiti.
    #
    # @param rules_filename: nome del file di configurazione
    # @param parser: definisce la grammatica da adoperare per poter effettuare il parsing del file
    # @param working_mem: La working memory iniziale che accoglierà i fatti letti e i template definiti
    # @param list_rules: La lista di regole definite
    # @param keyword_list: La lista di parole chiave della grammatica corrente
    # @param goal_state: Lo stato finale del problema corrente
    # @param global_vars: dizionario contenente le variabili globali definite nel file
    @staticmethod
    def _interpret_results(rules_filename, parser, working_mem, list_rules, keyword_list, goal_state, global_vars):
        try:
            result = parser.parseFile(rules_filename, parseAll=True)
            if not result:
                print('Empty file. Nothing will be loaded!')
            else:
                # Il dizionario non è vuoto, interpreta i risultati
                for keyword in keyword_list:
                    val = result.get(keyword, None)
                    if keyword == 'facts' and not val is None:
                        GrammarParser._interpret_facts(val, working_mem, global_vars)
                    elif keyword == 'template' and not val is None:
                        GrammarParser._interpret_template(val, working_mem, global_vars)
                    elif keyword == 'rule' and not val is None:
                        GrammarParser._interpret_rules(val, list_rules, global_vars)
                    elif keyword == 'final_state' and not val is None:
                        GrammarParser._interpret_final_state(goal_state, val[0], global_vars)
                    elif keyword == 'globals' and not val is None:
                        GrammarParser._interpret_globals(global_vars, val[1:])
        except ParseException as e:
            raise e

    ##
    # Permette di acquisire tutte le informazioni in merito alle variabili
    # globali definite nel file di configurazione
    @staticmethod
    def _interpret_globals(globals_vars, val):
        globals_vars.update({g[0]: g[1] for g in val})

    ##
    # Permette di interpretare i fatti acquisiti, trasformandoli in istanze della classe Fact
    # a partire dalla loro rappresentazione in stringa.
    #
    # @param fact_list: lista di fatti non strutturati (stringhe)
    # @param working_mem: istanza della classe WorkingMemory
    @staticmethod
    def _interpret_facts(fact_list, working_mem, globals_var):
        for raw_fact in fact_list:
            #curr_fact =Fact(raw_fact[0], attribute_list=[x for x in raw_fact[1:]])
            attribute_list = []

            for attr in raw_fact[1:]:
                #if '(' in attr[1] or ')' in attr[1]: # fatti con espressioni
                #    attr[1] = str(eval(attr[1]))
                if isinstance(attr, list):
                    if attr[1].startswith('?'):
                        # attr[0] - nome slot
                        # raw_fact - fatto grezzo
                        attr[1] = UIManager.get_input_from_user(working_mem, attr[0], raw_fact)
                    elif attr[1].startswith('global.'):
                        attr[1] = globals_var[attr[1][attr[1].index('?'):]]
                elif attr.startswith('global.'):
                    attr = globals_var[attr[attr.index('?'):]]

                attribute_list.append(attr)

            curr_fact = Fact(raw_fact[0], attribute_list=attribute_list)

            try:
                working_mem.add_fact(curr_fact)
            except WorkingMemoryException as ex:
                print('Fact not inserted: ', curr_fact)

    ###
    # Permette di interpretare le regole acquisite, trasformandole in istanze della classe Rule
    # a partire dalla loro rappresentazione in stringa.
    #
    # @param rules_list: lista di regole in forma testuale
    # @param list_rules: lista di oggetti istanza delle classe Rule
    @staticmethod
    def _interpret_rules(rules_list, list_rules, globals_var):
        def verify_variable_values(left_side_cond, right_side_cond):
            delim_index = 0
            defined_variables = []
            curr_state = False

            for cond in left_side_cond:
                if isinstance(cond, list):
                    if cond[0] == 'bind':
                        attr_list = cond[2][1:]
                    else:
                        attr_list = cond[1:]

                    for attr in attr_list:
                        if isinstance(attr, list):
                            if attr[1].startswith('?'):
                                defined_variables.append(attr[1])
                            elif attr[1].startswith('global.?'):
                                attr[1] = globals_var[attr[1][attr[1].index('?'):]]  # sostituisco la variabile globale
                        else:
                            if attr.startswith('?'):
                                defined_variables.append(attr)
                            elif attr.startswith('global.?'):
                                attr = globals_var[attr[attr.index('?'):]]  # sostituisco la variabile globale
                    delim_index += 1
                else:
                    if Utils.is_boolean_expr(cond):
                        break
            len_leftside = len(left_side_cond)
            if delim_index < len_leftside:
                len_def_variables = len(defined_variables)
                i = delim_index
                while i < len_leftside:
                    for key in globals_var:
                        if key in left_side_cond[i]:
                            left_side_cond[i] = left_side_cond[i].replace('global.' + key, globals_var[key])
                    var_id = Utils.capture_variables_id(left_side_cond[i])

                    if not len([x for x in var_id if x in defined_variables]) == len(var_id):
                        break  # vi è una variabile non definita!!!
                    i += 1

                if i == len_leftside:
                    curr_state = True
                else:
                    return False
            else:
                curr_state = True

            # parte sinistra corretta
            # controlla parte destra

            if curr_state:
                for attr in right_side_cond:
                    if attr[0] == 'assert':
                        for elem in attr[1][1:]:
                            if isinstance(elem, list):
                                if elem[1].startswith('?'):
                                    defined_variables.append(elem[1])
                                elif 'global.?' in elem[1]:
                                    for key in globals_var:
                                        if key in elem[1]:
                                            elem[1] = elem[1].replace('global.' + key, globals_var[key])
                                            #elem[1] = globals_var[elem[1][elem[1].index('?'):]] # sostituisco la variabile globale
                            else:
                                if elem.startswith('?'):
                                    defined_variables.append(elem)
                                elif elem.startswith('global.?'):
                                    elem = globals_var[elem[elem.index('?'):]]  # sostituisco la variabile globale

                    elif attr[0] == 'modify':
                        for elem in attr[2]:
                            if isinstance(elem, list):
                                if elem[1].startswith('?'):
                                    defined_variables.append(elem[1])
                                elif 'global.?' in elem[1]:
                                    for key in globals_var:
                                        if key in elem[1]:
                                            elem[1] = elem[1].replace('global.' + key, globals_var[key])
                                            #elem[1] = globals_var[elem[1][elem[1].index('?'):]] # sostituisco la variabile globale
                            else:
                                if elem.startswith('?'):
                                    defined_variables.append(elem)
                                elif elem.startswith('global.?'):
                                    elem = globals_var[elem[elem.index('?'):]]  # sostituisco la variabile globale

            return curr_state

        for rule in rules_list:
            # nessun errore nella definizione della regola
            # provvedo ad inserirla nel dizionario delle regole
            if verify_variable_values(rule[0], rule[1]):
                real_rule = Rule(rule[0], rule[1])
                list_rules[real_rule] = real_rule.actions
            else:
                raise ValueError('Unbinded variable in LHS')

    ##
    # Permette di interpretare i template presenti all'interno del file di configurazione,
    # trasformandoli dalla loro rappresentazione testuale in una forma gestibile del motore di
    # inferenza.
    #
    # @param parsed_value: rappresentazione testuale dei template nel file
    # @param wm: Working memory che accoglierà i template definiti
    @staticmethod
    def _interpret_template(parsed_value, wm, globals_var):
        for raw_template in parsed_value:
            curr_template = Template(raw_template[0])

            for raw_slot in raw_template[1:]:
                if isinstance(raw_slot, list):
                    for spec in raw_slot:
                        if isinstance(spec, list):
                            for i in range(len(spec)):
                                if spec[i].startswith('global.'):
                                    spec[i] = globals_var[spec[i][spec[i].index('?'):]]

                curr_template.add_slot(Slot(raw_slot))
            wm.add_template(curr_template)

    ##
    # Permette la corretta acqusizione dello stato finale presente nel file di
    # configurazione in forma testuale. Una volta acquisito lo stato finale diviene
    # un elemento del motore di inferenza necessario per la risoluzione del problema
    # @param goal_state: stato finale correttamente acquisito
    # @param parsed_goal_state: stato finale in forma testuale
    @staticmethod
    def _interpret_final_state(goal_state, parsed_goal_state, globals_var):
        goal_state.set_name(parsed_goal_state[0])
        for attr in parsed_goal_state[1:]:
            if isinstance(attr, list):
                if attr[1].startswith('global.?'):
                    attr[1] = globals_var[attr[1][attr[1].index('?'):]]
            else:
                if attr.startswith('global.'):
                    attr = globals_var[attr[attr.index('?'):]]

            goal_state.add_attribute(attr)