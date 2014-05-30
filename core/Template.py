from yaiep.core.Slot import Slot


class Template:
    def __init__(self, name):
        self._slots = {}
        self.name = name

    def add_slot(self, slot):
        if not isinstance(slot, Slot):
            raise ValueError

        self._slots[slot.name] = slot

    def get_slot_list(self):
        return self._slots

    def get_slot(self, name):
        return self._slots[name]

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