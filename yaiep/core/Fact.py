
class Fact:
    """
    Classe che rappresenta un fatto che verrà memorizzato all'interno
    della Working Memory
    Mediante la medesima struttura il sistema è in grado di gestire sia un
    fatto semplice e sia un template (fatto non ordinato)
    """
    def __init__(self, name, id=None, attribute_list=None):
        """
        Inizializza il fatto corrente impostando un nome ed
        eventualmente un identificativo e una lista di attributi

        @param name: Nome del fatto corrente
        @param id: identificativo del fatto corrente
        @param attribute_list: lista di attributi associata al fatto
        """
        self._attribute_list = attribute_list
        self._fact_name = name
        self._id = id

    def has_variable(self):
        """
        Controlla se il fatto corrente presenta
        fra i suoi attributi delle variabili
        """
        has_variable = False

        for attr in self._attribute_list:
            if isinstance(attr, list):
                if attr[1].startswith('?'):
                    has_variable = True
            else:
                if attr.startswith('?'):
                    has_variable = True

        return has_variable

    def get_attributes(self):
        """
        Restituisce la lista degli attributi del fatto corrente
        """
        return self._attribute_list

    def add_attribute(self, attribute):
        """
        Aggiunge un nuovo fatto alla lista degli attributi
        Se la lista dovesse essere vuota, il metodo provvede
        ad inizializzarla correttamente
        """
        if self._attribute_list is None:
            self._attribute_list = []
        self._attribute_list.append(attribute)

    def remove_attribute(self, attribute):
        """
        Rimuove dalla lista degli attributi del fatto corrente
        l'attributo specificato in input come parametro
        """
        self._attribute_list.remove(attribute)

    def get_name(self):
        """
        Restituisce il nome del fatto corrente
        """
        return self._fact_name

    def set_name(self, name):
        """
        Inizializza il nome del fatto corrente
        con quello specificato in input
        """
        self._fact_name = name

    def set_id(self, id):
        """
        Imposta l'identificativo del fatto corrente con quello
        specificato in input
        """
        self._id = id

    def get_id(self):
        """
        Restituisce l'identificativo associato dalla working memory
        al fatto corrente
        """
        return self._id

    def is_template(self):
        """
        Controlla se il fatto corrente è un fatto ordinato o non ordinato

        @return: True se il fatto è non-ordinato(template), False altrimenti
        """
        for attr in self._attribute_list:
            if isinstance(attr, list):
                return True # almeno un attributo di tipo lista di elementi
        return False

    def get_attribute_value(self, attr_name):
        """
        Restituisce il valore associato ad un determinato attributo
        del fatto corrente avente come nome quello specificato in input

        @param attr_name: nome dell'attributo del quale si intende ottenere il valore
        @return: Se attr_name è presente ritorna il valore effettivo associato all'attributo,
        altrimenti restituisce None
        """
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

        return self._attribute_list == other.get_attributes() \
            and self._fact_name == other.get_name()