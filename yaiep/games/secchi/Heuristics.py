

def miglior_secchio(wm):
    from yaiep.core.WorkingMemory import WorkingMemory
    assert isinstance(wm, WorkingMemory)

    fact_list = wm.get_fact_list()
    secchio_quattro = None
    for key in fact_list:
        fact = fact_list.get(key)
        fact_attr_nome = fact.get_attribute_value('nome')
        if fact.get_name() == 'secchio' and not fact_attr_nome is None and fact_attr_nome == 'secchio_da_quattro':
            secchio_quattro = fact

    quantita = secchio_quattro.get_attribute_value('quantita')

    return 4-int(quantita)



