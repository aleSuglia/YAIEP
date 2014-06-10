

##
# Classe che rappresenta una situazione eccezionale che può
# verificarsi nel momento in cui l'Interprete riceva in input un comando
# non significativo
class UnknownCommand(Exception):
    def __init__(self):
        Exception.__init__(self)
