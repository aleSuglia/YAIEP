##
# Classe che rappresenta un fatto che verrà memorizzato all'interno
# della Working Memory
# Mediante la medesima struttura il sistema è in grado di gestire sia un
# fatto semplice e sia un template (fatto non ordinato)
#
class Fact:
    ##
    # Inizializza il fatto corrente impostando un nome ed
    # eventualmente un identificativo e una lista di attributi
    #
    # @param name: Nome del fatto corrente
    # @param id: identificativo del fatto corrente
    # @param attribute_list: lista di attributi associata al fatto
    #
    def __init__(self, name, id=None, attribute_list=None):
        self._attribute_list = attribute_list
        self._fact_name = name
        self._id = id

    ##
    # Controlla se il fatto corrente presenta
    # fra i suoi attributi delle variabili
    #
    def has_variable(self):
        has_variable = False

        for attr in self._attribute_list:
            if isinstance(attr, list):
                if attr[1].startswith('?'):
                    has_variable = True
            else:
                if attr.startswith('?'):
                    has_variable = True

        return has_variable

    ##
    # Restituisce la lista degli attributi del fatto corrente
    #
    def get_attributes(self):
        return self._attribute_list

    ##
    # Rimpiazza la lista degli attributi corrente con quella specificata
    # come parametro
    #
    # @param attributes: nuova lista di attributi per il fatto corrente
    def set_attributes(self, attributes):
        self._attribute_list.clear()
        self._attribute_list.extend(attributes)

    ##
    # Aggiunge un nuovo fatto alla lista degli attributi
    # Se la lista dovesse essere vuota, il metodo provvede
    # ad inizializzarla correttamente
    #
    # @param attribute attributo da aggiungere alla lista degli attributi
    def add_attribute(self, attribute):
        if self._attribute_list is None:
            self._attribute_list = []
        self._attribute_list.append(attribute)

    ##
    # Rimuove dalla lista degli attributi del fatto corrente
    # l'attributo specificato in input come parametro
    #
    # @param attribute attributo da rimuovere dalla lista degli attributi
    def remove_attribute(self, attribute):
        self._attribute_list.remove(attribute)

    ##
    # Restituisce il nome del fatto corrente
    #
    # @return nome del fatto corrente
    def get_name(self):
        return self._fact_name

    ##
    # Inizializza il nome del fatto corrente
    # con quello specificato in input
    #
    # @parma name nuovo nome per il fatto corrente
    def set_name(self, name):
        self._fact_name = name

    ##
    # Imposta l'identificativo del fatto corrente con quello
    # specificato in input
    #
    # @param id nuovo id per il fatto corrente
    def set_id(self, id):
        self._id = id

    ##
    # Restituisce l'identificativo associato dalla working memory
    # al fatto corrente
    #
    #
    def get_id(self):
        return self._id

    ##
    # Controlla se il fatto corrente è un fatto ordinato o non ordinato
    #
    #@return: True se il fatto è non-ordinato(template), False altrimenti
    def is_template(self):
        for attr in self._attribute_list:
            if isinstance(attr, list):
                return True # almeno un attributo di tipo lista di elementi
        return False

    ##
    # Restituisce il valore associato ad un determinato attributo
    # del fatto corrente avente come nome quello specificato in input
    #
    # @param attr_name: nome dell'attributo del quale si intende ottenere il valore
    # @return: Se attr_name è presente ritorna il valore effettivo associato all'attributo,
    # altrimenti restituisce None
    #
    def get_attribute_value(self, attr_name):
        for attr in self._attribute_list:
            if attr[0] == attr_name:
                return attr[1]

        return None

    def __repr__(self):
        return 'Fact-{0}: {1} -> {2}'.format(self._id,
                                             self._fact_name,
                                             self._attribute_list)

    def __eq__(self, other):
        if not isinstance(other, Fact):
            return False

        res = self.is_template() + other.is_template()

        if res == 1:
            return False

        equal_attributes = True
        other_attributes = other.get_attributes()

        for fact in self._attribute_list:
            if not fact in other_attributes:
                equal_attributes = False
                break

        return equal_attributes and self._fact_name == other.get_name()