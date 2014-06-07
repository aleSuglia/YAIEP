# # Modulo che gestisce il motore di inferenza
import copy
import inspect
import sys
import types
from pyparsing import ParseException
from yaiep.core.Agenda import Agenda
from yaiep.core.Fact import Fact
from yaiep.core.UIManager import UIManager
from yaiep.core.Utils import Utils
from yaiep.core.WorkingMemory import WorkingMemory
from yaiep.core.WorkingMemoryException import WorkingMemoryException
from yaiep.grammar.EngineConfigFileParser import EngineConfigFileParser
from yaiep.grammar.GrammarParser import GrammarParser
from yaiep.graph.SearchGraph import SearchGraph
from yaiep.ml import KnowledgeAcquisition
from yaiep.ml.KAException import KAException
from yaiep.search.SearchMethodFactory import SearchMethodFactory


# #
# Asserisce un nuovo fatto aggiungendolo alla working memory
# @param wm working memory alla quale aggiungere il fatto
# @param params fatti da aggiungere alla working memory
# @param var_dict eventuali valori da associare alle variabili presenti nel fatto
#
def _make_assert(wm, params, var_dict=None):
    assert isinstance(wm, WorkingMemory)

    for fact in params:
        if not Utils.has_variable(fact):
            try:
                fact_attributes = fact[1:]
                for i in range(len(fact_attributes)):
                    if isinstance(fact_attributes[i], list):
                        fact_attributes[i][1] = str(eval(fact_attributes[i][1]))
                    else:
                        fact_attributes[i] = str(eval(fact_attributes[i]))

                wm.add_fact(Fact(fact[0], attribute_list=fact[1:]))
            except WorkingMemoryException as ex:
                print('Fact not inserted')
        else:
            solutions = Utils.substitute_variable(fact, var_dict)
            for sol in solutions:
                try:
                    for i in range(len(sol)):
                        if isinstance(sol[i], list):
                            if Utils.verify_symbol(sol[i][1]):
                                sol[i][1] = str(eval(sol[i][1]))
                        else:
                            if Utils.verify_symbol(sol[i]):
                                sol[i] = str(eval(sol[i]))
                        wm.add_fact(Fact(fact[0], attribute_list=sol))
                except WorkingMemoryException:
                    pass


# #
# Dalla documentazione Clips:
# The modify action allows the user to modify template facts on the fact-list. Only one fact may be
# modified with a single modify statement. The modification of a fact is equivalent to retracting
# the present fact and asserting the modified fact.
#
# @param wm: working memory sulla quale verrà effettuata l'operazione di modificata del fatto
# @param actions: rappresentazione sotto forma di lista dell'operazione da eseguire
# @param var_dict: eventuali variabili associate al fatto corrente
# @param var_bind: riferimento ai fatti da modificare
#
def _make_modify(wm, actions, var_dict=None, var_bind=None):
    assert isinstance(wm, WorkingMemory)

    bind_variable = actions[0]
    parameters = copy.deepcopy(actions[1])  # i parametri da modificare

    for i in range(len(parameters)):
        if isinstance(parameters[i], list):
            if Utils.verify_symbol(parameters[i][1]):
                if '?' in parameters[i][1]:
                    for key in var_dict:
                        parameters[i][1] = parameters[i][1].replace(key, list(var_dict[key])[0])
                parameters[i][1] = str(eval(parameters[i][1]))
        else:
            if Utils.verify_symbol(parameters[i]):
                if '?' in parameters[i]:
                    for key in var_dict:
                        parameters[i] = parameters[i].replace(key, list(var_dict[key])[0])
                parameters[i] = str(eval(parameters[i]))

    try:
        wm.modify_fact(bind_variable, parameters, var_dict, var_bind)
    except WorkingMemoryException as wme:
        print('Fact not modified: ', wme.value)


##
# Esegue un'operazione sulla working memory che fa in modo
# di rimuovere un fatto che è stato precedentemente referenziato
# in una regola
#
# @param wm: working memory sulla quale eseguire l'operazione di rimozione del fatto
# @param actions: rappresentazione sotto forma di lista dell'operazione da eseguire
# @param var_bind: riferimento al fatto da rimuovere
#
def _make_retract(wm, actions, var_bind=None):
    assert isinstance(wm, WorkingMemory)

    bind_variable = actions[0]
    old_list_fact_id = actions[1:]  # indirizzi numerici o con variabili
    complete_list_fact_id = None  # indirizzi numerici
    fact_list = wm.get_fact_list()

    # sostituisco alle variabili "matchate" gli indirizzi
    # relativi ai fatti della working memory

    if var_bind:
        complete_list_fact_id = []
        for fact_id in old_list_fact_id:
            if fact_id.startswith('?'):
                complete_list_fact_id.extend(var_bind[fact_id])
            else:
                complete_list_fact_id.append(fact_id)
    else:
        complete_list_fact_id = old_list_fact_id

    for fact_id in complete_list_fact_id:
        if fact_id in range(0, len(fact_list)):
            curr_fact = fact_list[fact_id]
            fact_list.remove(curr_fact)
        else:
            raise WorkingMemoryException('WM Exception: Unable to remove fact, wrong fact id used')


##
# Classe che modella nella sua interezza la logica del motore d'inferenza
#
#
class InferenceEngine:
    ## @var lista di comandi che può effettuare la working memory
    _command_list_wm = {
        'assert': _make_assert,
        'modify': _make_modify,
        'retract': _make_retract
    }

    _heuristics_module = 'Heuristics'
    _graphic_module = 'Graphics'
    _configuration_file = 'conf_file'

    def _load_external_function(self, problem_filesystem):
        sys.path.append(problem_filesystem)

        try:
            import Heuristics

            heur_module = locals()
            self._heuristics = {x[0]: x[1] for x in inspect.getmembers(heur_module[InferenceEngine._heuristics_module])
                                if isinstance(x[1], types.FunctionType)}

            self._graphic_functions = {x[0]: x[1] for x in inspect.getmembers(heur_module[InferenceEngine._graphic_module])
                                if isinstance(x[1], types.FunctionType)}
        except ImportError:
            pass  # modulo per le funzioni euristiche non presente

        try:
            import Graphics

            graphic_module = locals()
            self._graphic_functions = {x[0]: x[1] for x in inspect.getmembers(graphic_module[InferenceEngine._graphic_module])
                                if isinstance(x[1], types.FunctionType)}
        except ImportError:
            pass  # modulo per le funzioni euristiche non presente


    ##
    # Provvede ad inizializzare tutti gli elementi presenti all'interno
    # del motore inferenziale
    #
    def __init__(self):
        self._wm = WorkingMemory()  # lo stato iniziale della working memory
        self._list_rules = []
        self._goal_state = [] # Fact("")
        self._global_vars = {}
        self._agenda = None
        self._heuristics = None
        self._conf_attributes = None
        self._graphic_functions = None
        self._init_fact_list = []
        self._step_state = []  # Opened, Closed, Nodo corrente

    ##
    # Permette il caricamento, dal file di configurazione,
    # di tutte le regole, dei fatti e della definizione di eventuali euristiche
    # per il problema corrente ed inoltre permette di caricare tutte le configurazioni
    # iniziali per poter scegliere alcune logiche specifiche del motore inferenziale
    #
    # @param conf_filename nome del file di configurazione del motore
    # @param def_filename nome del file di definizione del problema
    def load_engine(self, problem_path):
        # Effettua il caricamento delle informazioni necessarie al motore di inferenza
        try:
            def_filename = problem_path + self._configuration_file
            settings_filename = problem_path + EngineConfigFileParser.DEFAULT_SETTINGS_FILENAME

            self._conf_attributes = EngineConfigFileParser.read_configuration_attribute(settings_filename)
            self._load_external_function(problem_path)

            # Effettua il caricamento del file di definizione del problema
            try:
                GrammarParser.load_grammar(def_filename, self._wm, self._list_rules, self._goal_state,
                                           self._global_vars, self._init_fact_list)
                self._agenda = Agenda(self._list_rules.copy())
            except ParseException as e:
                msg = str(e)
                complete_msg = "%s: %s" % (msg, e.line)
                print(complete_msg)
                print(" " * (len("%s: " % msg) + e.loc) + "^^^")
                raise e

        except ParseException as parse_ex:
            print('Your engine\'s configuration file seems broken :(')
            raise parse_ex
        except ValueError as value_ex:
            print('{0} -> {1}'.format(value_ex.args[0], value_ex.args[1]))
            raise value_ex

    def __str__(self):
        return "{0}\nRULE LIST: {1}\nAGENDA: {2}\nGOAL STATE: {3}".format(str(self._wm),
                                                                          str(self._list_rules),
                                                                          str(self._agenda),
                                                                          str(self._goal_state))

    ##
    # Verifica se il motore inferenziale è stato inizializzato correttamente
    # ed è pronto per poter avviare la risoluzione del problema
    #
    # @return True se il motore inferenziale è stato inizializzato, False altrimenti
    def is_ready(self):
        return not self._agenda is None

    ##
    # Restituisce la rappresentazione in forma di stringa
    # dei fatti attualmente definiti nella working memory del motore inferenziale
    #
    # @return string-form della working memory del motore
    def fact_list(self):
        return str(self._wm)

    ##
    # Restituisce la rappresentazione in forma di stringa
    # delle regole attualmente definite del motore inferenziale
    #
    # @return string-form della lista delle regole
    def rule_list(self):
        string_form = ""
        i = 1
        for rule in self._list_rules:
            string_form += "{0} - {1}\n".format(str(i), str(rule))
            i += 1

        return string_form

    ##
    # Verifica se una determinata regole è in grado di
    # alterare lo stato della working memory permettendo
    # la riattivazione di una regola già utilizzata
    #
    # Operazioni come retract e modify sono in grado di alterare la working memory
    # @param rule regole da verificare
    # @return True se la regola è in grado di modificare la working memory, False altrimenti
    def modify_working_mem(self, rule):
        if isinstance(rule, tuple):
            for act in rule[0].actions.actions:
                if act[0] == 'modify' or act[0] == 'retract':
                    return True
            return False
        else:
            for act in rule.actions.actions:
                if act[0] == 'modify' or act[0] == 'retract':
                    return True
            return False

    def apply_action(self, wm, rule):
        if isinstance(rule, tuple):  # regole aventi nella parte sinistra delle variabili
            var_dict = rule[1]
            actions = rule[0].actions
            var_bind = rule[2] if len(rule) == 3 else None
            for action in actions.actions:
                if action[0] == 'assert':
                    InferenceEngine._command_list_wm['assert'](wm, action[1:], var_dict)
                elif action[0] == 'modify':
                    InferenceEngine._command_list_wm['modify'](wm, action[1:], var_dict, var_bind)
                elif action[0] == 'retract':
                    InferenceEngine._command_list_wm['retract'](wm, action[1:], var_bind)
        else:
            actions = rule.actions
            for action in actions.actions:
                if action[0] == 'assert':
                    InferenceEngine._command_list_wm['assert'](wm, action[1:])
                elif action[0] == 'modify':
                    InferenceEngine._command_list_wm['modify'](wm, action[1:])
                elif action[0] == 'retract':
                    InferenceEngine._command_list_wm['retract'](wm, action[1:])

    ##
    # Avvia la risoluzione del problema caricato a partire dallo stato attuale
    # della working memory e delle regole presenti
    #
    # Il metodo una volta invocato permette di ispezionare lo spazio di ricerca
    # secondo un metodo ben definito di ricerca (informata o non informata)
    # dando la possibilità all'utente di ritrovare tutte le soluzioni o parte di esse
    def solve_problem(self):
        # Se sono disponibili tutte le informazioni per poter avviare la procedura
        # di risoluzione del problema
        if self._init_fact_list and self._conf_attributes:
            self._wm.clear_facts()
            self._load_init_configuration()
            graph = SearchGraph(self._wm)
            search_type = self._conf_attributes['search_type']
            search_method = None

            if search_type == 'depth':

                if 'graphics' in self._conf_attributes:
                    graphic_func_name = self._conf_attributes['graphics']
                    if self._graphic_functions and graphic_func_name in self._graphic_functions:
                        search_method = SearchMethodFactory.generate_search_method(search_type,
                                                                           graph, self._agenda, self._goal_state,
                                                                           self._graphic_functions[graphic_func_name])
                    else:
                        search_method = SearchMethodFactory.generate_search_method(search_type,
                                                                           graph, self._agenda, self._goal_state, None)

                else:
                    search_method = SearchMethodFactory.generate_search_method(search_type,
                                                                           graph, self._agenda, self._goal_state, None)
            else:
                ref_heur_function = None
                ref_graph_function = None

                if 'graphics' in self._conf_attributes:
                    graphic_func_name = self._conf_attributes['graphics']
                    if self._graphic_functions and graphic_func_name in self._graphic_functions:
                        ref_graph_function = self._graphic_functions[graphic_func_name]

                if 'heuristic' in self._conf_attributes:
                    heur_func_name = self._conf_attributes['heuristic']
                    if self._heuristics and heur_func_name in self._heuristics:
                        ref_heur_function = self._heuristics[heur_func_name]

                search_method = SearchMethodFactory.generate_search_method(search_type, graph, self._agenda,
                                                                           self._goal_state,
                                                                           ref_graph_function,
                                                                           ref_heur_function)

            sol_state = search_method.execute(self)


            if sol_state:
                search_method.print_solution_path()

            # ripristina l'agenda per poter garantire un nuovo avvio del problema
            self._agenda = Agenda(self._list_rules.copy())

            return sol_state

    def solve_problem_step(self, new_solution):
        if new_solution:
            if not self._step_state and self._init_fact_list and self._conf_attributes:
                self._wm.clear_facts()
                self._load_init_configuration()
                graph = SearchGraph(self._wm)
                search_type = self._conf_attributes['search_type']
                search_method = None

                if search_type == 'depth':

                    if 'graphics' in self._conf_attributes:
                        graphic_func_name = self._conf_attributes['graphics']
                        if self._graphic_functions and graphic_func_name in self._graphic_functions:
                            search_method = SearchMethodFactory.generate_search_method(search_type,
                                                                               graph, self._agenda, self._goal_state,
                                                                               self._graphic_functions[graphic_func_name])
                        else:
                            search_method = SearchMethodFactory.generate_search_method(search_type,
                                                                               graph, self._agenda, self._goal_state, None)

                    else:
                        search_method = SearchMethodFactory.generate_search_method(search_type,
                                                                               graph, self._agenda, self._goal_state, None)
                else:
                    ref_heur_function = None
                    ref_graph_function = None

                    if 'graphics' in self._conf_attributes:
                        graphic_func_name = self._conf_attributes['graphics']
                        if self._graphic_functions and graphic_func_name in self._graphic_functions:
                            ref_graph_function = self._graphic_functions[graphic_func_name]

                    if 'heuristic' in self._conf_attributes:
                        heur_func_name = self._conf_attributes['heuristic']
                        if self._heuristics and heur_func_name in self._heuristics:
                            ref_heur_function = self._heuristics[heur_func_name]

                    search_method = SearchMethodFactory.generate_search_method(search_type, graph, self._agenda,
                                                                               self._goal_state,
                                                                               ref_graph_function,
                                                                               ref_heur_function)

                # 0 - opened nodes
                # 1 - closed nodes
                # 2 - init state
                # 3 - search method
                # 4 - curr_node
                # 5 - path index
                self._step_state = [[], [], self._wm, search_method, self._wm, 0]

                return search_method.step_execute(self, self._step_state[0], self._step_state[1], self._step_state[2])
            else:
                self._step_state[4] = self._wm # inizia di nuovo dalla root nella ricerca
                return self._step_state[3].step_execute(self, self._step_state[0], self._step_state[1], self._step_state[2])

    def get_step_state(self):
        return self._step_state

    def clear_step(self):
        self._step_state.clear()

    def print_step_solution(self):
        if self._step_state:
            self._step_state[4] = self._step_state[3].print_step_solution(self._step_state[4], self._step_state[5])
            if not self._step_state[4] is None:
                  return True
            else:
                self._step_state[5] += 1
                return False

        return False

    def reset(self):
        self._wm = WorkingMemory()  # lo stato iniziale della working memory
        self._list_rules = []
        self._goal_state = []
        self._global_vars = {}
        WorkingMemory.fact_id_counter = 0
        self._agenda = None
        self._heuristics = None
        self._conf_attributes = None
        self._graphic_functions = None
        self._init_fact_list.clear()

    def _load_init_configuration(self):
        copy_init = copy.deepcopy(self._init_fact_list)

        for fact in copy_init:
            attributes = fact.get_attributes()
            for attr in attributes:
                if isinstance(attr, list):
                    if attr[1].startswith('?'):
                        # attr[0] - nome slot
                        # raw_fact - fatto grezzo
                        attr[1] = UIManager.get_input_from_user(self._wm, attr[0], fact, True)
                else:
                    attr = UIManager.get_input_from_user(self._wm, attr, fact, False)
            self._wm.add_fact(fact)


    ##
    # Invoca il tool di apprendimento automatico (C.5) per poter acquisire da un dataset
    # in formato arff delle regole nel formato valido per il motore inferenziale
    #
    # @param dataset_filename nome del dataset a partire dal quale verrano generate le regole
    def learn_rules_from_dataset(self, dataset_filename):
        try:
            KnowledgeAcquisition.knowledge_acquisition(self._list_rules, dataset_filename)
        except KAException as ex:
            print("Unable to start machine learning process: " + ex.args)
