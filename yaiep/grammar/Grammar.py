
class Grammar:
    """
    Rappresenta una classe astratta che definisce le struttura portante
    di una grammatica supportata dal motore di inferenza
    """
    def get_grammar_definition(self):
        """
        Restituisce l'oggetto che permetterà di effettuare il parsing del file di
        configurazione secondo la sintassi adottata dal motore di inferenza
        @return: parser per la grammatica corrente
        """
        pass

    def get_keyword_list(self):
        """
        Restituisce l'insieme delle parole chiavi previste dalla grammatica corrente
        @return: lista delle parole chiavi in formato di testuale
        """
        pass

