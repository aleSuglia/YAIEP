from yaiep.core.Fact import Fact
from yaiep.core.Template import Template
from yaiep.core.WorkingMemoryException import WorkingMemoryException
import copy

# #
# Classe che rappresenta l'intera struttura di una Working Memory
# che viene adoperata per poter rappresentare uno stato dello spazio di ricerca
#
# Una Working Memory terrà traccia di quelli che sono i fatti presenti e della
# struttura di quelli che sono i fatti non ordinati presenti all'interno della working memory
class WorkingMemory:
    fact_id_counter = 0

    # #
    # Inizializza la lista dei fatti e i riferimenti
    # alla struttura dei template
    #
    def __init__(self):
        self._fact_list = {}
        self._templates = {}

    # #
    # Aggiunge il template specificato in input
    # alla lista dei template definiti
    #
    # @param template: struttura del fatto non ordinato da aggiungere
    #
    def add_template(self, template):
        if not isinstance(template, Template):
            raise WorkingMemoryException
        self._templates[template.name] = template

    # #
    # Restituisce la lista dei fatti attualmente definiti
    # sotto forma di dizionario.
    # Il dizionario restituito avrà come chiave l'id internamente
    # associato dalla working memory al fatto nel momento dell'inserimento
    # e come valore la struttura del fatto stessa.
    #
    def get_fact_list(self):
        return self._fact_list

    # #
    # Restituisce la lista contenente una struttura specifica per
    # ogni fatto non ordinato presente nella Working Memory
    #
    def get_templates(self):
        return self._templates

    # #
    # Verifica se il fatto specificato in input risulta
    #  essere presente nella Working Memory
    #
    #  @param fact: fatto da controllare
    #  @return True se il fatto risulta essere già presente nella Working Memory
    #  False altrimenti
    #
    def fact_already_present(self, fact):
        if not self._is_template(fact):
            return fact in self._fact_list.values()
        else:
            for curr_fact in [x for x in self._fact_list.values() if x.get_name() in self._templates and x.get_name() == fact.get_name()]:
                curr_fact_attributes = sorted(curr_fact.get_attributes(), key=lambda item: item[0])
                new_fact_attributes = sorted(fact.get_attributes(), key=lambda item: item[0])
                if curr_fact_attributes == new_fact_attributes:
                    return True
            return False

    def _is_template(self, fact):
        if not isinstance(fact, Fact):
            raise ValueError

        return True if fact.get_name() in self._templates else False


    # #
    # Modifica il fatto corrente rimpiazzando con i parametri specificati
    # in input, i valori specifici del fatto corrente
    #
    # @param bind_variable: variabile che è stata utilizzata per legare il fatto corrente
    # @param parameters: parametri che verranno modificati con associati valori
    # @param var_dict: eventuali variabili con i rispettivi valori ammissibili
    # @param var_bind: dizionario che presenta i fatti legati alle variabili
    #
    def modify_fact(self, bind_variable, parameters, var_dict, var_bind):
        # controlla se i fatti da modificare sono dei template
        mod_facts = var_bind[bind_variable]

        def check_template_facts(facts):
            for fact_id in facts:
                if not self._is_template(self._fact_list[fact_id]):
                    return False

            return True

        if not check_template_facts(mod_facts):
            raise WorkingMemoryException('WM Exception: Unable to modify an unordered fact.')

        def inner_modify_fact(fact, parameters, var_dict):
            old_parameters = fact.get_attributes()
            new_parameters = [x for x in old_parameters if not x[0] in [param[0] for param in parameters]]
            new_fact = Fact(fact.get_name())

            for param in new_parameters:
                new_fact.add_attribute(param)

            for param in parameters:
                new_fact.add_attribute(param)

            return new_fact

        try:
            for fact_id in mod_facts:
                curr_fact = self._fact_list[fact_id]

                self.remove_fact(curr_fact)
                curr_fact = inner_modify_fact(curr_fact, parameters, var_dict)
                self.add_fact(curr_fact)
        except WorkingMemoryException as wme:
            raise wme

    # #
    # Aggiunge il fatto specificato in input alla Working memory corrente
    #
    # Nel caso in cui vi sia un qualche tipo di anomalia nell'inserimento
    # dei fatti, il metodo provvede a rilevare l'anomali correttamente e a
    # propagare l'errore all'esterno.
    #
    # @param fact: fatto da aggiungere alla Working Memory
    #
    def add_fact(self, fact):
        if not isinstance(fact, Fact):
            raise WorkingMemoryException('WM Exception: Wrong argument type')
        # Se il fatto corrente non è un template allora controlla che non sia già presente
        if not self._is_template(fact):
            # Fatto con il medesimo nome già presente. Lancia eccezione
            if self.fact_already_present(fact):
                raise WorkingMemoryException('WM Exception: Fact already inserted.')
        else: # fatto non ordinato
            try:
                curr_template = self._templates[fact.get_name()]
                mod_attributes = fact.get_attributes()
                curr_template.save_attributes(mod_attributes)
                if self.fact_already_present(fact):
                    raise WorkingMemoryException('WM Exception: Fact already inserted.')
            except ValueError as ex:
                raise WorkingMemoryException(str(ex))

        fact.set_id(WorkingMemory.fact_id_counter)
        WorkingMemory.fact_id_counter += 1
        self._fact_list[fact.get_id()] = fact

    # #
    # Verifica se il fatto specificato in input
    # corrisponde ad uno dei fatti presente nella Working Memory corrente
    #
    # @param new_fact: fatto che si intende controllare
    # @return id del fatto che ha fatto match con quello specificato in input
    #
    def match_fact(self, new_fact):
        def inner_match_fact(new_fact):
            for fact in self._fact_list.values():
                if fact == new_fact:
                    return fact.get_id()
            return None

        if not self._is_template(new_fact):
            return inner_match_fact(new_fact)
        else:
            for curr_fact in [x for x in self._fact_list.values() if x.get_name() in self._templates and x.get_name() == new_fact.get_name()]:
                curr_fact_attributes = sorted(curr_fact.get_attributes(), key=lambda item: item[0])
                new_fact_attributes =  sorted(new_fact.get_attributes(), key=lambda item: item[0])
                if self._intersect_multiple_lists(new_fact_attributes, curr_fact_attributes):
                    return curr_fact.get_id()

            return None

    def _intersect_multiple_lists(self, first, sec):

        if len(first) < len(sec):
            return len([elem for elem in first if elem in sec]) == len(first)
        else:
            return len([elem for elem in sec if elem in first]) == len(first)

    # #
    # Rimuove il fatto specificato dalla Working memory
    # @param fact istanza della classe Fact o intero che rappresenta l'id del fatto
    #
    # @throw WorkingMemoryException se il fatto non dovesse essere presente
    def remove_fact(self, fact):
        if isinstance(fact, Fact):
            self._fact_list.pop(fact.get_id())
        elif isinstance(fact, int):
            self._fact_list.pop(fact)
        else:
            raise WorkingMemoryException('WM Exception: Wrong argument type')

    def __str__(self):
        fact_list_str = ''
        for fact in self._fact_list.values():
            fact_list_str += str(fact) + '\n'

        repr_str = 'DEFINED FACTS: \n' + fact_list_str +\
                   '\nTotal number of facts: ' + str(len(self._fact_list))

        repr_str += '\n\nDEFINED TEMPLATES: \n' + str(self._templates)
        return repr_str

    def __eq__(self, other):
        if not isinstance(other, WorkingMemory):
            return False

        curr_facts = sorted(self._fact_list.values(), key=lambda fact : fact.get_name())
        other_facts = sorted(other.get_fact_list().values(), key=lambda fact : fact.get_name())


        return curr_facts == other_facts

    def __hash__(self):
        return hash(str(self._fact_list) + str(self._templates))

    # #
    # Permette di effettuare una copia completa della working memory
    # corrente
    #
    # @return una nuova istanza di WorkingMemory che possiede i medesimi
    # elementi di quella corrente
    #
    def copy(self):
        return copy.deepcopy(self)