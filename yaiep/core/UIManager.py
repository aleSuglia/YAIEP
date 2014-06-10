from genericpath import isfile
import os
from os.path import isdir
from yaiep.core.WorkingMemory import WorkingMemory


##
# Fornisce un modo per poter garantire all'utente un'interazione più amichevole
# con il motore inferenziale
#
class UIManager:
    ##
    # Richiede dei parametri all'utente per poter configurare la working memory
    # @param wm: working memory da settare con i parametri immessi
    #
    @staticmethod
    def get_input_from_user(wm, *params):
        assert isinstance(wm, WorkingMemory)
        is_template = params[2]
        curr_value = None

        if is_template:
            slot_name = params[0]
            fact = params[1]

            templates_dict = wm.get_templates()
            fact_name = fact.get_name()

            if fact_name in templates_dict:
                defined_template = templates_dict[fact_name]
                curr_slot = defined_template.get_slot(slot_name)
                curr_value = input('Insert value for \'{0}\' in {1} \n'
                                   '(be careful to the following constraints - type({2}) / range ({3}) : '.\
                                   format(slot_name, fact,
                                          curr_slot.type if curr_slot.type else None,
                                          curr_slot.range if curr_slot.range else None))
                while not curr_slot.check_slot_value(curr_value):
                    print('Incorrect value specified...')
                    curr_value = input('Insert value for \'{0}\' in {1} \n'
                                       '(be careful to the following constraints - type({2}) / range ({3}) : '.\
                                   format(slot_name, fact,
                                          curr_slot.type if curr_slot.type else None,
                                          curr_slot.range if curr_slot.range else None))
        else:
            attr_id = params[0]
            fact = params[1]
            fact_attributes = fact.get_attributes()
            len_attr = len(fact_attributes)
            curr_value = []
            for i in range(len_attr):
                curr_value.append(input('Insert value for \'{0}\' in {1}->{2}: '.format(fact_attributes[i], fact.get_name(), fact.get_attributes())))

        return curr_value

    ##
    # Richiede all'utente se vuole proseguire la ricerca delle soluzione al problema preso in analisi
    #
    @staticmethod
    def continue_search():
        value = input('Are you satisfied with this solution? (y/n): ')
        if value == 'n':
            return True
        else:
            return False

    ##
    # Richiede all'utente quale puzzle caricare in memoria
    #
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
                    return GAMES_DIR + os.sep + games[choosed] + os.sep, DEFAULT_CONF_FILE
                except Exception as ex:
                    print('An error occurs :(')
                print("--------------------------------")
                print()
            except (ValueError, TypeError):
                return None, None
