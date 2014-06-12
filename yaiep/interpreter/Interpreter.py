## Modulo che gestisce l'interprete dei comandi inseriti dall'utente
import os
from pyparsing import Literal, Word, alphas, ParseException, Optional
from yaiep.core.InferenceEngine import InferenceEngine
from yaiep.core.UIManager import UIManager
from yaiep.interpreter.UnknownCommand import UnknownCommand


##
# Stampa a video l'elenco dei fatti presenti nel motore inferenziale
# @param engine: motore inferenziale contenente i fatti
#
def _do_facts(engine):
    if not engine.is_ready():
        pass
    else:
        print(engine.fact_list())


##
# Stampa a video l'elenco delle regole presenti nel motore inferenziale
# @param engine: motore inferenziale contenente le regole
#
def _do_rules(engine):
    if not engine.is_ready():
        pass
    else:
        print(engine.rule_list())


##
# Permette di scegliere il puzzle da risolvere e predispone il motore inferenziale all'avvio della risoluzione
# del puzzle
# @param engine: motore inferenziale che sarà successivamente configurato
#
def _do_load(engine):
    if engine.is_ready:
        # rimuove i dati dell'ultima esecuzione
        engine.reset()

    chosen_game_path, conf_file_name = UIManager.select_game()
    if chosen_game_path:
        try:
            print('### LOAD ENGINE STATUS ###')
            engine.load_engine(chosen_game_path)
            print('### Insert \'(run)\' or \'(step)\' if you want to start the game ###')
        except Exception:
            print('### Please fix the problems found and load again the engine using (load) command ###')


##
# Avvia la risoluzione del problema permettendo
# all'utente di vedere ogni singolo passo del cammino solutivo
# e di interagire con lo stesso modificando la situazione corrente
# del sistema
#
def _do_step(engine):
    assert isinstance(engine, InferenceEngine)

    if not engine.is_ready():
        print('No data are present...')
    else:

        step_state = engine.get_step_state()

        if not step_state:
            is_solution = engine.solve_problem_step(True)
            if not engine.get_step_state()[3].get_solution()[0]:
                print('The specified configuration is useless!')
                engine.clear_step()
                return

            if is_solution:
                engine.print_step_solution()
                answer = input('Do you want to insert another initial configuration? (y/n): ')
                if answer == 'y':
                    engine.clear_step()
                    engine.solve_problem_step(True)
                    engine.print_step_solution()

        else:
            if not engine.print_step_solution():
                is_solution = engine.solve_problem_step(True)
                if not engine.get_step_state()[3].get_solution()[0]:
                    print('The specified configuration is useless!')
                    engine.clear_step()
                    return
                if is_solution:
                    print('-----------------------------------------------------------------------------------------------')
                    if step_state[5] != len(step_state[3].get_path_to_solution()):
                        engine.print_step_solution()
                        answer = input('Do you want to insert another initial configuration? (y/n): ')
                        if answer == 'y':
                            engine.clear_step()
                            engine.solve_problem_step(True)
                            engine.print_step_solution()
                    else:
                        print('No more solutions')
                        engine.clear_step()
            else:
                answer = input('Do you want to insert another initial configuration? (y/n): ')
                if answer == 'y':
                    engine.clear_step()
                    engine.solve_problem_step(True)


##
# Risolve il puzzle scelto verificando prima se il motore è stato correttamente configurato
# @param engine: motore inferenziale con cui si risolverà il puzzle
#
def _do_run(engine):
    if not engine.is_ready():
        print('No data are present...')
    else:
        if not engine.solve_problem():
             print('No solution found!')


##
# Carica le regole presenti in un dataset che soddisfa una determinata configurazione
# @param engine: motore inferenziale nella quale le regole saranno caricate
# @param param: dataset dal quale prelevare le regole
#
def _do_learn(engine, param):
    if not engine.is_ready():
        pass
    else:
        engine.learn_rules_from_dataset(param)


##
# Resetta tutti i campi del motore inferenziale
# @param engine: motore inferenziale i cui campi verranno resettati
#
def _do_reset(engine):
    if engine.is_ready():
        engine.reset()


##
# Stampa a video un testo nel quale è presente la spiegazione del funzionamento e interfacciamento del motore
# inferenziale
#
def _do_help():
    command_list_help = banner + '''
        The symbol '>>>' indicates that the interpreter is waiting
        for a command to be inserted in the console.
        After that, it will be able to execute what you've requested.
        For a complete reference of the commands available see the section
        @command_list.

        ### command_list ###
        (facts) - displays the list of facts contained in the Working Memory
        (rules) - displays the available rules
        (run) - solves the loaded problem
        (step) - solves the loaded problem step-by-step
        (load) - grants to the user to load a game which is saved in a specific
        folder whose name is 'games'. For each game, there is a dedicated folder
        with all the configuration file needed for the execution of the inference engine
        (See user guide documentation for more information).
        (learn_rules) - runs a machine learning algorithm on a specified
        dataset (in ARFF format) in order to learn some other rules

        (reset) - removes all the data loaded so far

        (exit) - closes the interpreter's session

        ----------------------------------------------------------------

    '''

    print(command_list_help)

valid_command = Literal('load') | Literal('facts') | Literal('rules') | \
                Literal('help') | Literal('exit') | Literal('learn_rules') | Literal('run') |\
                Literal('reset') | Literal('step')

banner = '''
        ----------------------------------------------------------------
        ###     YAIEP - Yet Another Inference Engine in Python      ###
        ----------------------------------------------------------------
'''

_command_list_interpreter = {
    'load': _do_load,
    'facts': _do_facts,
    'rules': _do_rules,
    'learn_rules': _do_learn,
    'help': _do_help,
    'run': _do_run,
    'reset': _do_reset,
    'step': _do_step
}

_console_command = Literal('(').suppress() + valid_command + \
                   Optional(Word(alphas + os.sep + '._-')) + Literal(')').suppress()


##
# Rappresenta la classe principale a partire dalla quale
# l'utente è in grado di avviare il motore inferenziale e procedere
# nella risoluzione di un gioco
#
class Interpreter:
    def __init__(self):
        self.engine = InferenceEngine()

    def _execute_command(self, command):
        if command[0] == 'exit':
            return True

        if command[0] == 'help':
            _do_help()
        else:
            command_len = len(command)

            if command_len != 1 and command_len != 2:
                raise UnknownCommand

            if command_len == 1:  # unary operator
                executor = _command_list_interpreter[command[0]]
                executor(self.engine)
            elif command_len == 2:  # binary operator
                executor = _command_list_interpreter[command[0]]
                executor(self.engine, command[1])
        return False

    ##
    # Avvia l'interprete dando la possibilità all'utente di inserire
    # delle istruzioni per poter effettuare il caricamento dei dati
    # necessari al motore per poter eseguire le proprie operazioni
    def start(self):
        print(banner)
        exit_flag = False
        try:
            while not exit_flag:
                line = input('>>> ')
                try:

                    result = _console_command.parseString(line)
                    exit_flag = self._execute_command(result)
                except (ParseException, UnknownCommand):
                    print('Invalid command inserted...')
                except (Exception, TypeError) as ex:
                    print('Something goes wrong :(\n< {0} >'.format(str(ex)))
        except KeyboardInterrupt:
            pass