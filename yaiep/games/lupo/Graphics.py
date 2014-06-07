from yaiep.core.WorkingMemory import WorkingMemory


def graphics(wm):
    assert isinstance(wm, WorkingMemory)

    def print_side(side_attributes):
        zero_attr = [x for x in side_attributes if x[1] == '0']
        one_attr = [x for x in side_attributes if x[1] == '1']

        right_side = " "

        for attr in zero_attr:
            if attr[0] == 'barcaiolo':
                right_side += " B "
            elif attr[0] == 'lupo':
                right_side += " L "
            elif attr[0] == 'pecora':
                right_side += " P "
            elif attr[0] == 'cavolo':
                right_side += " C "

        left_side = " "

        for attr in one_attr:
            if attr[0] == 'barcaiolo':
                left_side += " B "
            elif attr[0] == 'lupo':
                left_side += " L "
            elif attr[0] == 'pecora':
                left_side += " P "
            elif attr[0] == 'cavolo':
                left_side += " C "

        #print("%20.20s||||||%20s" % (left_side, right_side))
        print('{0} ||||| {1}'.format(left_side.center(10), right_side.center(10)))

    fact_list = wm.get_fact_list()
    sponda = None

    for fact_id in fact_list:
        fact = fact_list[fact_id]
        if fact.get_name() == 'sponda_sx':
            sponda = fact
            break

    print_side(sponda.get_attributes())


