from yaiep.core.Slot import Slot


##
# Classe che rappresenta un fatto non ordinato nella
# sua interezza. Ogni fatto ordinato è paragonabile
# ad una struttura del C, il quale può prevedere
# dei campi (chiamati SLOT) ai quali è associato un nome
# ed eventualmente delle restrizioni sui valori che esso
# può assumere.
# Un template può avere un nome il quale, all'interno della
# WM deve essere univoco.
# A partire da tale template, più fatti che rispettano la sua
# struttura potranno essere generati senza generare alcun tipo
# di conflitto.
class Template:
    def __init__(self, name):
        self._slots = {}
        self.name = name

    ##
    # Aggiunge un nuovo slot al template corrente.
    # Affinchè esso possa essere aggiunto è necessario che il valore
    # specificato in input sia un'istanza della classe Slot.
    #
    # @param slot: nuovo slot da aggiungere al template
    def add_slot(self, slot):
        assert isinstance(slot, Slot)

        self._slots[slot.name] = slot

    ##
    # Restituisce l'intera lista di slot
    # presenti all'interno del template corrente
    #
    # @return dizionario avente come chiave il nome dello slot e come valore un'istanza
    # della classe slot
    def get_slot_list(self):
        return self._slots

    ##
    # Restituisce lo slot avente come nome
    # quello specificato in input al metodo
    #
    # @param name nome della slot da acquisire
    # @return istanza della classe Slot
    def get_slot(self, name):
        return self._slots[name]

    ##
    # Provvede a modificare la lista di valori
    # che rappresentano la struttura di base per quello che sarà
    # un nuovo fatto non ordinato, effettuando opportuni controlli
    # di consistenza.
    # Tali controlli vengono effettuati considerando le informazioni
    # presenti in ogni slot del template.
    #
    # @param attributes lista degli attributi da modificare
    def save_attributes(self, attributes):
        examined_attr = []

        # controlla la correttezza degli attributi
        for attr in attributes:
            if attr[0] in examined_attr:
                raise ValueError('Duplicated slot name ', attr[0])
            else:
                curr_slot = self._slots.get(attr[0], None)
                if curr_slot is None:
                    raise ValueError('Incorrect slot name ', attr[0])
                if not curr_slot.check_slot_value(attr[1]):  # check type consistency
                    raise ValueError('Incorrect type for slot ', attr[0])
                examined_attr.append(attr[0])

        # controllo valori non presenti
        # potrebbe essere necessario impostare i valori di default
        all_slots = set(self._slots.keys())
        curr_slots = [attr[0] for attr in attributes]

        all_slots.difference_update(curr_slots)

        # a questo punto setta i valori di default per ogni slot
        for slot_name in all_slots:
            curr_slot = self._slots[slot_name]
            if not curr_slot.default_value is None:
                attributes.append([slot_name, curr_slot.default_value])
            else:
                attributes.append([slot_name, None])

    def __repr__(self):
        return str('{0}'.format(str(self._slots)))

    def __eq__(self, other):
        if not isinstance(other, Template):
            return False

        return self.name == other.name and self._slots == other.get_slot_list()