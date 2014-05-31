from genericpath import isfile
import os
from os.path import isdir
from yaiep.core.WorkingMemory import WorkingMemory

# #
# Fornisce un modo per poter garantire all'utente un'interazione più amichevole
# con il motore inferenziale
#
class UIManager:
    @staticmethod
    def get_input_from_user(wm, *params):
        assert isinstance(wm, WorkingMemory)
        slot_name = params[0]
        raw_fact = params[1]

        templates_dict = wm.get_templates()

        if raw_fact[0] in templates_dict:
            defined_template = templates_dict[raw_fact[0]]
            curr_slot = defined_template.get_slot(slot_name)
            curr_value = input('Insert value for \'{0}\' in {1} \n'
                               '(be careful to the following constraints - type({2}) / range ({3}) : '.\
                               format(slot_name, raw_fact,
                                      curr_slot.type if curr_slot.type else None,
                                      curr_slot.range if curr_slot.range else None))
            while not curr_slot.check_slot_value(curr_value):
                print('Incorrect value specified...')
                curr_value = input('Insert value for \'{0}\' in {1} \n'
                                   '(be careful to the following constraints - type({2}) / range ({3}) : '.\
                               format(slot_name, raw_fact,
                                      curr_slot.type if curr_slot.type else None,
                                      curr_slot.range if curr_slot.range else None))

            return curr_value

    @staticmethod
    def continue_search():
        value = input('Are you satisfied with this solution? (y/n): ')
        if value == 'n':
            return True
        else:
            return False

    @staticmethod
    def select_game():
        GAMES_DIR = 'games'
        DEFAULT_CONF_FILE = 'conf_file'

        games = [x for x in os.listdir(GAMES_DIR) if
                 isdir(GAMES_DIR + "/" + x) and isfile(GAMES_DIR + "/" + x + "/" + DEFAULT_CONF_FILE)]

        if len(games) < 1:
            print("No games are present in the default directory (Do you have put them in the folder \'games\'?)")
            return False

        while True:

            print("Available games:")
            for i, game in enumerate(games):
                print("\t" + str(i) + ") " + str(game))

            try:
                choosed = int(input('Select the puzzle that you want to solve: '))
                print("You have chosen: " + str(games[choosed]))
                print()
                print("--------------------------------")
                try:
                    return GAMES_DIR + os.sep + games[choosed] + os.sep + DEFAULT_CONF_FILE
                except Exception as ex:
                    print('An error occurs :(')
                print("--------------------------------")
                print()
            except ValueError:
                return None
