from yaiep.core.Fact import Fact
from yaiep.core.OrderMethod import OrderRulesMethod, SalienceAdder, DepthAdder, RandomAdder
from yaiep.core.Utils import Utils

# #
# Verifica se un paramentro e' il nome di una funzione di bind
# @param param: parametro da verificare
# @return True se param è uguale a "bind", False altrimenti
#
def is_function_name(param):
    return param == "bind"


# #
# Classe rappresentante l'agenda nella quale saranno organizzate
# le regole attivate e non ancora usate e gestisce il metodo d'ordine con cui essere verrano
# attivate
#
class Agenda:

    # #
    # Inizializza l'agenda corrente impostando le regole attivate, le regole non usate e
    # il metodo di ordinamento d'attivazione
    # @param all_rules: tutte le regole presenti nel file di configurazione
    # @param order_method: metodo di ordinamento da utilizzare di default è impostata la SALIENCE
    #
    def __init__(self, all_rules, order_method=OrderRulesMethod.SALIENCE):
        self._activated_rules = []  # regole ATTIVATE
        self._not_used_rules = all_rules
        self._order_method = None
        self._init_order(order_method)

    # #
    # Inizializza il metodo di ordinamento
    # @param order_method: metodo di ordinamento
    #
    def _init_order(self, order_method):
        if order_method == OrderRulesMethod.SALIENCE:
            self._order_method = SalienceAdder()
        elif order_method == OrderRulesMethod.DEPTH:
            self._order_method = DepthAdder()
        else:
            self._order_method = RandomAdder()

    # #
    # Imposta una regola come attivata rimuovendola dall'elenco delle regole non usate ed aggiungendola
    # nell'elenco delle regole attivate
    # @param rule_fired: regola da attivare
    #
    def set_activated_rule(self, rule_fired):
        self._not_used_rules.remove(rule_fired)
        self._activated_rules.append(rule_fired)

    # #
    # Verifica se l'elenco di attributi di un fatto contiene un'espresssione da valutare
    # @param fact_attributes: elenco di attributi da valutare
    # @return True se l'attributo corrente presenta un simbolo di una espressione, False
    # se nessun attributo dell'elenco contiene simboli
    #
    def _contains_expression(self, fact_attributes):
        for attr in fact_attributes:
            for elem in attr:
                if Utils.verify_symbol(elem):
                    return True

        return False

    # #
    # Valuta un'espressione presente nell'attributo corrente modificandone il valore
    # @param int_dict: struttura contenente tutte le varibili presenti nell'espressione con
    # annessi valori
    #
    def _evaluate_expression(self, int_dict):
        if isinstance(int_dict, dict):
            for key in int_dict.keys():
                curr_attributes = int_dict.get(key)
                for attr in curr_attributes:
                    if '(' in attr or ')' in attr:
                        attr = str(eval(attr))
        else:
            for i in range(0,len(int_dict)):
                for j in range(1, len(int_dict[i])):
                    if Utils.verify_symbol(int_dict[i][j]):
                        int_dict[i][j] = str(eval(int_dict[i][j]))

    # #
    # Effettua il matching tra i fatti presenti nella working memory corrente e
    # quelli presenti nelle condizioni delle regole presenti nel motore
    # @param wm: working memory contenente i fatti
    # @param list_rules: elenco delle regole presenti nel motore inferenziale
    #
    def _do_matching(self, wm, list_rules):
        conflict_set = []  # lista delle regole attivabili (ordinate in base al criterio di ordinamento)
        fact_list = wm.get_fact_list()

        for rule in list_rules:
            activable_rule = True
            i = 0
            cond_list = rule.conditions.conditions
            var_dict = {}
            var_bind = {}

            while activable_rule and i < len(cond_list):
                bind_key = None
                request_evaluation = False
                temp_fact = None
                if is_function_name(cond_list[i][0]):
                    temp_fact = Fact(cond_list[i][2][0], attribute_list=cond_list[i][2][1:])
                    bind_key = cond_list[i][1]
                    var_bind[bind_key] = []
                elif isinstance(cond_list[i], str) and Utils.is_boolean_expr(cond_list[i]):
                    if '?' in cond_list[i]:
                        gen_expressions = Utils.substitute_variable_string(cond_list[i], var_dict)
                        activable_rule = sum([1 for expr in gen_expressions if eval(expr)]) > 0

                    else:
                        activable_rule = eval(cond_list[i])
                     #   i += 1
                else:
                    temp_fact = Fact(cond_list[i][0], attribute_list=cond_list[i][1:])

                if temp_fact and self._contains_expression(temp_fact.get_attributes()):
                    request_evaluation = True

                if temp_fact and temp_fact.has_variable():
                    int_dict, is_template = self._get_variable_values(temp_fact, fact_list, var_bind, bind_key)
                    # if richiesta_valutazione allora valuta ogni espressione presente
                    if request_evaluation:
                        self._evaluate_expression(int_dict)
                    if not self._verify_var_dict(var_dict, temp_fact, int_dict, is_template):
                        activable_rule = False
                    #else:
                    #    i += 1
                elif temp_fact:
                    if request_evaluation:
                        self._evaluate_expression(temp_fact.get_attributes())
                    matched_fact_id = wm.match_fact(temp_fact)
                    if matched_fact_id is None:
                        activable_rule = False
                    else:
                      #  i += 1
                        if bind_key:
                            var_bind[bind_key].append(matched_fact_id)

                i += 1
            if activable_rule:
                if var_dict:
                    if var_bind:
                        self._order_method.add(conflict_set, (rule, var_dict, var_bind))  # rule and matching variables
                    else:
                        self._order_method.add(conflict_set, (rule, var_dict))
                else:
                    if var_bind:
                        self._order_method.add(conflict_set, (rule, None, var_bind))
                    else:
                        self._order_method.add(conflict_set, rule)

            if var_dict:
                var_dict = {}

            if var_bind:
                var_bind = {}

        return conflict_set

    # #
    #
    # Avvalora tutte le varibili di bind e di espressioni presenti nel
    # file di configurazione salvando i loro nomi in appositi dizionari ed associandogli i loro valori reali
    # e verifica se un fatto è un template
    # @param fact: fatto da verificare se è un template
    # @param fact_list: elenco dei fatti i cui attributi potrebbero contenere variabili da avvalorare
    # @param var_bind: dizionario contenente tutte le variabili delle funzioni di bind
    # @param key: chiave di bind il cui valore deve essere avvalorato
    # @return dizionario delle variabile delle espressioni e True se il fatto è un template altrimanti False
    #
    @staticmethod
    def _get_variable_values(fact, fact_list, var_bind, key):
        fact_attributes = fact.get_attributes()
        if isinstance(fact_attributes[0], list):
            is_template = True
            fact_attributes = sorted(fact_attributes, key=lambda item: item[0])
        else:
            is_template = False

        # memorizza i valori associati alle variabili appartenenti al fatto corrente
        int_dict = {}

        for curr_fact_id in fact_list:  # for each fact in WM, try to match fact
            curr_fact = fact_list[curr_fact_id]
            if curr_fact.get_name() == fact.get_name():  # if they have the same name
                curr_fact_attributes = curr_fact.get_attributes()

                if is_template and isinstance(curr_fact_attributes[0], list):
                    curr_fact_attributes = sorted(curr_fact_attributes, key=lambda item: item[0])
                    both_template = True
                elif not (is_template and isinstance(curr_fact_attributes[0], list)):
                    both_template = False
                else:
                    continue

                if both_template:
                    temp_dict = {attr[0]: attr[1] for attr in curr_fact_attributes}
                    i = 0
                    fact_attributes_len = len(fact_attributes)
                    while i != fact_attributes_len:
                        attr = fact_attributes[i]
                        if attr[1].startswith('?'):  # variable found, match with real value
                            if attr[1] in int_dict:
                                if not temp_dict[attr[0]] in int_dict[attr[1]]:
                                    int_dict[attr[1]].append(temp_dict[attr[0]])
                            else:
                                int_dict[attr[1]] = [temp_dict[attr[0]]]
                        else:
                            if attr[1] != temp_dict[attr[0]]:
                                break
                        i += 1
                    if i == fact_attributes_len:
                        if not key is None:
                            var_bind[key].append(curr_fact.get_id())

                else:
                    if len(fact_attributes) == len(curr_fact_attributes):  # ...and the same number of attributes
                        i = 0
                        fact_attributes_len = len(fact_attributes)
                        while i != fact_attributes_len:
                            if fact_attributes[i].startswith('?'):  # variable found, match with real value
                                if fact_attributes[i] in int_dict:
                                    # non mettere due volte lo stesso valore
                                    if not curr_fact_attributes[i] in int_dict[fact_attributes[i]]:
                                        int_dict[fact_attributes[i]].append(curr_fact_attributes[i])
                                else:
                                    int_dict[fact_attributes[i]] = [curr_fact_attributes[i]]

                            else:
                                if fact_attributes[i] != curr_fact_attributes[i]:
                                    break
                            i += 1
                        if i == fact_attributes_len:
                            if not key is None:
                                var_bind[key].append(curr_fact.get_id())

        return int_dict, is_template

    # #
    # Verifica se tutte le variabili delle espressioni sono state matchate con un valore esistente
    # se il match è stato completato avvalora il dizionario delle variabili completo
    # @param var_dict: dizionario da avvalorare se il match va a buon fine
    # @param fact: fatto con cui effettuare il match dei valori del dizionario delle variabili delle espressioni
    # @param is_template: valore booleano che indica se il fatto è un template
    # @return True se il match va a buon fine, False altrimenti
    #
    def _verify_var_dict(self, var_dict, fact, int_dict, is_template):
        # A questo punto aggiorno il dizionario globale per poter mantenere i valori validi
        if not var_dict:
            if not self._complete_match(fact, int_dict, is_template):
                return False
            var_dict.update(int_dict)
        else:
            if not self._complete_match(fact, int_dict, is_template):
                return False

            # Per ogni chiave in comune
            for key in set(var_dict.keys()).intersection(int_dict.keys()):
                # aggiorno il valore associato alla chiave corrente
                var_dict[key] = set(var_dict[key]).intersection(int_dict[key])

            for key in set(int_dict.keys()).difference(var_dict.keys()):
                var_dict[key] = int_dict[key]

        return True  # Processo completo

    # #
    # Verifica se ci sono regole attivabili
    # @return True se ci sono regole attivabili, False altrimenti
    #
    def has_activable_rule(self):
        return True if self._not_used_rules else False

    # #
    # Effettua il match completo tra il fatto corrente e il dizionario delle variabili
    # @param curr_fact: fatto con cui fare il match delle variabili
    # @param var_dict: dizionario contenente le variabili del fatto avvalorate
    # @param is_template: True se il fatto è un template, False altrimenti, di default è False
    # @return False se non ci sono variabile da matchare, True altrimenti
    #
    def _complete_match(self, curr_fact, var_dict, is_template=False):
        if not var_dict:
            return False  # no matched variables

        lhs_variables = None

        if is_template:
            lhs_variables = {x[1] for x in curr_fact.get_attributes() if x[1].startswith('?')}
        else:
            lhs_variables = {x for x in curr_fact.get_attributes() if x.startswith('?')}

        # Non vi è stato un match con tutte le variabili
        if lhs_variables != var_dict.keys():
            return False

        for key in var_dict:
            if not var_dict[key]:
                return False  # no match for a variable

        return True

    # #
    # Ritorna la prima regola attivabile
    # @param wm: working memory con cui verrà effettuato il match delle regole
    # @return None se non ci sono regole da attivare, altrimenti la prima attivabile
    #
    def get_activable_rule(self, wm):
        conflict_set = self._do_matching(wm, self._not_used_rules)
        return None if not conflict_set else conflict_set[0]

    # #
    # Ripristina le regole che sono nuovamente attivabile in seguito ad una modifica della working memory
    # @param wm: working memory eventualmente modificata
    #
    def restore_rules(self, wm):
        restored_rules = self._do_matching(wm, self._activated_rules)
        #self._not_used_rules.extend([rule[0] if isinstance(rule, tuple) else rule for rule in restored_rules])
        for rule in restored_rules:
            if isinstance(rule, tuple):
                if not rule[0] in self._not_used_rules:
                    self._not_used_rules.append(rule[0])
            else:
                if not rule in self._not_used_rules:
                    self._not_used_rules.append(rule)

    # #
    # Ritorna tutte le regole attivabili
    # @param wm: working memory con cui verrà effettuato il match delle regole
    # @return None se non ci sono regole da attivare, altrimenti l'elenco delle regole ativabili
    #
    def get_activable_rules(self, wm):
        return self._do_matching(wm, self._not_used_rules)

    def __str__(self):
        return str(self._activated_rules)

