from pyparsing import alphas, Word, Literal, Keyword, OneOrMore, ParseException, Group



# #
# Classe specifica che permette di acquisire
# tutte le informazioni presenti all'interno del
# file di configurazione necessarie per poter inizializzare
# correttamente i differenti componenti del motore inferenziale
# Le opzioni attualmente disponibili per poter configurare il file sono le seguenti
# (possono essere le uniche voci presenti all'interno del file di configurazione):
# - heuristic: permette di definire il nome della funzione euristica che si intende adoperare
# per la risoluzione del problema (tale funzione dovrà essere definita nell'apposito file Heuristics.py)
# - search_type: permette di specificare il tipo di metodo di ricerca da adottare (valori supportati 'depth', 'astar')
# - graphics: definisce la funzione da adoperare per poter permettere di visualizzare in maniera
# più comprensibile le regole che vengono prodotte dal sistema nel momento in cui risolve un
# determinato gioco
class EngineConfigFileParser:
    _config_keyword = Keyword('heuristic') | Keyword('search_type') | Keyword('graphics')
    _configuration_attribute = Group(Literal('(').suppress() + \
                                     _config_keyword + Word(alphas) + Literal(')').suppress())

    _config_file_definition = OneOrMore(_configuration_attribute)
    DEFAULT_SETTINGS_FILENAME = 'settings'

    ##
    # Restituisce i parametri di configurazione specificati
    # per poter predisporre il motore inferenziale alla corretta
    # risoluzione del problema corrente
    #
    # Il percorso del gioco dovrà prevedere un file (formattato correttamente)
    # avente come nome 'settings' il quale verrà utilizzato per poter estrapolare
    # gli attributi e memorizzarli all'interno del sistema in una struttura opportuna.
    #
    # @param game_settings_file path di sistema nel quale è presente il file di configurazione dell'engine
    # @return struttura contenente i parametri di configurazione impostati
    @staticmethod
    def read_configuration_attribute(game_settings_file):
        attribute_dict = {}
        try:
            results = EngineConfigFileParser._config_file_definition.parseFile(game_settings_file)

            for attribute in results:
                if attribute[0] == 'search_type' and (attribute[1] != 'depth' and attribute[1] != 'astar'):
                    raise ValueError('Invalid value for search_type: ', attribute[1])
                attribute_dict[attribute[0]] = attribute[1]

            return attribute_dict
        except ParseException as parse_ex:
            #print('Your settings file is broken :(')
            raise parse_ex