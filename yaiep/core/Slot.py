from pyparsing import alphas, Word, nums, ParseException


##
# Classe che rappresenta uno slot di un fatto non ordinato (template)
# Tale slot prevede un nome ed un preciso valore. Tale valore potrebbe essere
# soggetto a delle restrizioni che possono essere imposte specificando il tipo
# dello slot (string o integer) oppure specificando un range nel quale può variare
# il valore nel caso in cui si tratta di un valore intero.
# E' possibile prevedere un valore di default che verrebbe impostato nel caso
# in cui non venisse specificato alcun tipo di valore per lo slot corrente nel momento
# della definizione del template
#
class Slot:
    ##
    # Provvede ad inizializzare lo slot corrente
    # con le informazioni specificate in input effettuando
    # opportuni controlli di consistenza dei tipi e di definizione
    # dei valori.
    #
    def __init__(self, params):
        self.name = ""
        self.type = None
        self.default_value = None
        self.range = None

        if isinstance(params, list):
            self.name = params[0]
            for attr in params[1:]:
                if attr[0] == 'default':
                    self.default_value = attr[1]
                elif attr[0] == 'type':
                    assert attr[1] == 'string' or attr[1] == 'integer'
                    self.type = attr[1]
                elif attr[0] == 'range':
                    self.range = [attr[1], attr[2]]
                    if int(self.range[0]) >= int(self.range[1]):
                        raise ValueError('Invalid range')

            if not self.default_value is None:
                try:
                    # consistenza di tipo sui valori dello slot corrente
                    parser = Word(alphas) if self.type == 'string' else Word(nums)
                    parser.parseString(self.default_value)
                    # se slot corrente ha un range definito
                    if not self.range is None:
                        spec_range = '{0} >= {1} and {0} <= {2}'.format(self.default_value, self.range[0], self.range[1])
                        if not eval(spec_range):
                            raise ValueError('Default value doesn\'t satisfy range constraints')
                except ParseException:
                    raise ValueError('Incorrect default value for slot')
        else:
            self.name = params

    ##
    # Effettua un controllo di consistenza sul valore specificato
    # in input rispetto alle restrizioni fissate per lo slot corrente
    #
    def check_slot_value(self, slot_value):
        try:
            if not self.type is None:
                parser = Word(alphas) if self.type == 'string' else Word(nums)
                parser.parseString(slot_value)
            if not self.range is None and self.type != 'string':
                spec_range = '{0} >= {1} and {0} <= {2}'.format(slot_value, self.range[0], self.range[1])
                if not eval(spec_range):
                    return False
            return True
        except ParseException:
            return False

    def __repr__(self):

        return '[name: {0}, type: {1}, def_value: {2}, range: {3}-{4}]'.format(self.name, self.type, self.default_value,
                                                                               self.range[0], self.range[1]) \
                if not self.range is None else \
                    '[name: {0}, type: {1}, def_value: {2}, range: None]'.format(self.name, self.type, self.default_value)

    def __eq__(self, other):
        if not isinstance(other, Slot):
            return False

        return self.default_value == other.default_value and self.name == other.name and self.type == other.type \
                and self.range == other.range