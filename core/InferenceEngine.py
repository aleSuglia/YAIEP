## Modulo che gestisce il motore di inferenza
import inspect
import sys
import types
from pyparsing import ParseException
from yaiep.core.Agenda import Agenda
from yaiep.core.Fact import Fact
from yaiep.core.Utils import Utils
from yaiep.core.WorkingMemory import WorkingMemory
from yaiep.core.WorkingMemoryException import WorkingMemoryException
from yaiep.grammar.GrammarParser import GrammarParser
from yaiep.graph.SearchGraph import SearchGraph
from yaiep.ml import KnowledgeAcquisition
from yaiep.ml.KAException import KAException
from yaiep.search.SearchMethodFactory import SearchMethodFactory


def _make_assert(wm, params, var_dict=None):
    """
    Asserisce un nuovo fatto aggiungendolo alla working memory
    @param wm working memory alla quale aggiungere il fatto
    @param params fatti da aggiungere alla working memory
    @param var_dict eventuali valori da associare alle variabili presenti nel fatto
    """
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


def _make_modify(wm, actions, var_dict, var_bind):
    """
    Dalla documentazione Clips:
    The modify action allows the user to modify template facts on the fact-list. Only one fact may be
    modified with a single modify statement. The modification of a fact is equivalent to retracting
    the present fact and asserting the modified fact.
    @param wm: working memory sulla quale verrà effettuata l'operazione di modificata del fatto
    @param actions: rappresentazione sotto forma di lista dell'operazione da eseguire
    @param var_dict: eventuali variabili associate al fatto corrente
    @param var_bind: riferimento ai fatti da modificare
    """

    assert isinstance(wm, WorkingMemory)

    bind_variable = actions[0]
    parameters = actions[1] # i parametri da modificare

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


def _make_retract(wm, actions, var_bind):
    """
    Esegue un'operazione sulla working memory che fa in modo
    di rimuovere un fatto che è stato precedentemente referenziato
    in una regola

    @param wm: working memory sulla quale eseguire l'operazione di rimozione del fatto
    @param actions: rappresentazione sotto forma di lista dell'operazione da eseguire
    @param var_bind: riferimento al fatto da rimuovere
    """
    assert isinstance(wm, WorkingMemory)

    bind_variable = actions[0]
    old_list_fact_id = actions[1:] # indirizzi numerici o con variabili
    complete_list_fact_id = None # indirizzi numerici
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


class InferenceEngine:
    """
    Classe che modella nella sua interezza la logica del motore d'inferenza
    """

    ## @var lista di comandi che può effettuare la working memory
    _command_list_wm = {
        'assert': _make_assert,
        'modify': _make_modify,
        'retract': _make_retract
    }

    _heuristics_module = 'Heuristics'
    _configuration_file = 'conf_file'

    def _load_heuristics(self, problem_filesystem):
        sys.path.append(problem_filesystem)
        try:
            import Heuristics
            heur_module = locals()
            self._heuristics = {x[0]:x[1] for x in inspect.getmembers(heur_module[InferenceEngine._heuristics_module])
                if isinstance(x[1], types.FunctionType)}
        except ImportError:
            pass # modulo per le funzioni euristiche non presente

    def __init__(self):
        self._wm = WorkingMemory() # lo stato iniziale della working memory
        self._list_rules = {}
        self._goal_state = Fact("")
        self._global_vars = {}
        self._agenda = None
        self._heuristics = None

    def load_engine(self, def_filename):
        try:
            GrammarParser.load_grammar(def_filename, self._wm, self._list_rules, self._goal_state, self._global_vars)
            self._agenda = Agenda(self._list_rules.copy())
        except ParseException as e:
            msg = str(e)
            complete_msg = "%s: %s" % (msg, e.line)
            print(complete_msg)
            print(" " * (len("%s: " % msg) + e.loc) + "^^^")

    def __str__(self):
        return "{0}\nRULE LIST: {1}\nAGENDA: {2}\nGOAL STATE: {3}".format(str(self._wm),
                                                         str(self._list_rules),
                                                         str(self._agenda),
                                                         str(self._goal_state))

    def is_ready(self):
        return not self._agenda is None

    def fact_list(self):
        return str(self._wm)

    def rule_list(self):
        return str(self._list_rules)

    def modify_working_mem(self, rule):
        """
        Controlla se la regola corrente è in grado di modificare la working memory
        @param rule regole da controllare
        """
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

    def matched_goal_state(self):
        return self._wm.match_fact(self._goal_state)


    def start_recognize_act_cycle(self):
        ## Avvia il ciclo di recognize-act del motore per poter procedere nell'attivazione
        #  delle regole immesse dall'utente
        no_more_rule = False

        while self._agenda.has_activable_rule() and not self.matched_goal_state() and not no_more_rule:
            complete_rule = self._agenda.get_activable_rule(self._wm)
            if complete_rule:
                self.apply_action(self._wm, complete_rule)  # assert, modify, retractx
                fired_rule = complete_rule[0] if isinstance(complete_rule, tuple) else complete_rule
                if self.modify_working_mem(fired_rule):
                    self._agenda.restore_rules(self._wm)  # reinserire regole già attivate nella lista di regole non attivate

                self._agenda.set_activated_rule(fired_rule)
            else:
                no_more_rule = True


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

    def solve_problem(self):
        if self._wm.get_fact_list():
            graph = SearchGraph(self._wm)
            search_method = SearchMethodFactory.generate_search_method('depth', graph, self._agenda, self._goal_state)
            sol_state = search_method.execute(self)

            if sol_state:
                return True

            return False

    def learn_rules_from_dataset(self, dataset_filename):
        try:
            KnowledgeAcquisition.knowledge_acquisition(self._list_rules, dataset_filename)
        except KAException as ex:
            print("Unable to start machine learning process: " + ex.args)
