from yaiep.search.AStarSearch import AStarSearch
from yaiep.search.DepthSearch import DepthSearch


def make_depth(factory_data):
    return DepthSearch(factory_data[0], factory_data[1], factory_data[2], factory_data[3])


def make_astar(factory_data):
    return AStarSearch(factory_data[0], factory_data[1], factory_data[2], factory_data[3], factory_data[4])


class SearchMethodFactory:
    factory_function = {
        'depth' : make_depth,
        'astar' : make_astar
    }

    @staticmethod
    def generate_search_method(class_name, *factory_data):
        if not class_name in SearchMethodFactory.factory_function:
            raise ValueError('Invalid search method specified')
        if len(factory_data) == 0:
            raise ValueError('Invalid factory data specified')

        return SearchMethodFactory.factory_function[class_name](factory_data)
