

def miglior_secchio(wm):
    from yaiep.core.WorkingMemory import WorkingMemory
    assert isinstance(wm, WorkingMemory)

    fact_list = wm.get_fact_list()
    secchio_quattro = None
    for key in fact_list:
        fact = fact_list.get(key)

        if fact.get_name() == 'secchio_da_quattro':
            secchio_quattro = fact

    value = int(secchio_quattro.get_attribute_value('quantita'))

    return 2-value



