

##
# Classe che definisce uno stato eccezionale che si può verificare
# nel caso in cui il metodo di acquisizione della conoscenza dovesse fallire
class KAException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)