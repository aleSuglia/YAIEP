from yaiep.search.AStarSearch import AStarSearch
from yaiep.search.DepthSearch import DepthSearch


def _make_depth(factory_data):
    return DepthSearch(factory_data[0], factory_data[1], factory_data[2], factory_data[3])


def _make_astar(factory_data):
    return AStarSearch(factory_data[0], factory_data[1], factory_data[2], factory_data[3], factory_data[4])


##
# Classe che permette di creare una nuova istanza di uno specifico
# metodo di ricerca senza essere direttamente a conoscenza di come
# il metodo di ricerca è stato implementato
#
class SearchMethodFactory:
    factory_function = {
        'depth' : _make_depth,
        'astar' : _make_astar
    }

    @staticmethod
    def generate_search_method(class_name, *factory_data):
        if not class_name in SearchMethodFactory.factory_function:
            raise ValueError('Invalid search method specified')
        if len(factory_data) == 0:
            raise ValueError('Invalid factory data specified')

        return SearchMethodFactory.factory_function[class_name](factory_data)
