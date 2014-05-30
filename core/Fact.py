
class Fact:
    def __init__(self, name, id=None, attribute_list=None):
        self._attribute_list = attribute_list
        self._fact_name = name
        self._id = id

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

    def get_attributes(self):
        return self._attribute_list

    def add_attribute(self, attribute):
        if self._attribute_list is None:
            self._attribute_list = []
        self._attribute_list.append(attribute)

    def remove_attribute(self, attribute):
        self._attribute_list.remove(attribute)

    def get_name(self):
        return self._fact_name

    def set_name(self, name):
        self._fact_name = name

    def set_id(self, id):
        self._id = id

    def get_id(self):
        return self._id

    def is_template(self):
        for attr in self._attribute_list:
            if isinstance(attr, list):
                return True # almeno un attributo di tipo lista di elementi
        return False

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

        return self._attribute_list == other.get_attributes() \
            and self._fact_name == other.get_name()