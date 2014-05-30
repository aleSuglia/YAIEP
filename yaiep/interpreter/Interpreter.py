import os
from pyparsing import Literal, Word, alphas, ParseException, Optional
from yaiep.core.InferenceEngine import InferenceEngine
from yaiep.interpreter.UnknownCommand import UnknownCommand


def _do_facts(engine):
    if not engine.is_ready():
        pass # nothing to do
    else:
        # param is useless
        print(engine.fact_list())


def _do_rules(engine):
    if not engine.is_ready():
        pass
    else:
        print(engine.rule_list())


def _do_load(engine, param):
    engine.load_engine(param)


def _do_run(engine):
    if not engine.is_ready():
        print('No data are present...')
    else:
        if not engine.solve_problem():
             print('No solution found!')


def _do_learn(engine, param):
    if not engine.is_ready():
        pass
    else:
        engine.learn_rules_from_dataset(param)


def _do_help():
    command_list_help = banner + '''
        The symbol '>>>' indicates that the interpreter is waiting
        for a command to be inserted in the console.
        After that, it will be able to execute what you've requested.
        For a complete reference of the commands available see the section
        @command_list.

        @command_list

        'facts' - displays the list of facts contained in the WM
        'rules' - displays the available rules
        'run' - start a recognize-act cycle
        'load' - grants the user to load a script which contains the
        definition of facts and rules (a path should be specified as
        an argument to the command e.g. (load /home/user/my_script.txt))
        'learn_rules' - runs a machine learning algorithm on a specified
        dataset (in ARFF format) in order to learn some other rules

        'exit' - closes the interpreter's session

        ----------------------------------------------------------------

    '''

    print(command_list_help)

valid_command = Literal('load') | Literal('facts') | Literal('rules') | \
                Literal('help') | Literal('exit') | Literal('learn_rules') | Literal('run')

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
    'run': _do_run
}

_console_command = Literal('(').suppress() + valid_command + \
                   Optional(Word(alphas + os.sep + '._')) + Literal(')').suppress()


class Interpreter:

    def __init__(self):
        self.engine = InferenceEngine()

    def execute_command(self, command):
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

    def start(self):
        print(banner)
        exit_flag = False
        try:
            while not exit_flag:
                line = input('>>> ')
                try:
                    result = _console_command.parseString(line)
                    exit_flag = self.execute_command(result)
                except (ParseException, UnknownCommand, TypeError):
                    print('Invalid command inserted...')
                except Exception as ex:
                    print('Something goes wrong :(\n< {0} >'.format(ex.args[1]))
        except KeyboardInterrupt:
            pass