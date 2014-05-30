class Utils:
    @staticmethod
    def has_variable(fact):
        """
        Controlla se la rappresentazione sotto forma di lista degli attributi un fatto, presenta
        delle variabili
        @param fact: lista di attributi di un fatto
        """
        for attr in fact:
            if isinstance(attr, list):
                for att in attr:
                    if att.startswith('?'):
                        return True
            elif attr.startswith('?'):
                return True

        return False

    @staticmethod
    def verify_symbol(attr):

        if '+' in attr \
            or '-' in attr \
            or '*' in attr \
            or '/' in attr \
                :
                return True

        return False

    @staticmethod
    def substitute_var_rec(solutions, var_dict, curr_list, missing_var, var_index):
        """
        Funzione di supporto per poter effettuare la sostituzione delle variabili
        con i loro rispettivi valori
        @param solutions lista di combinazioni corrette generate
        @param var_dict valori da associare alle variabili
        @param curr_list combinazione che si sta generando
        @param missing_var variabili non ancora ispezionate
        @param var_index posizione nel pattern delle variabili
        """

        if not Utils.has_variable(curr_list):
            solutions.append(curr_list[:])
        else:
            next_var = missing_var[0]
            if isinstance(missing_var[0], list):  #template
                for val in var_dict[next_var[1]]:
                    index = var_index[next_var[1]]
                    if isinstance(index, list):
                        for curr_index in index:
                            curr_list[curr_index] = val
                    else:
                        curr_list[var_index[next_var[1]]] = [next_var[0], val]
                    Utils._substitute_var_rec(solutions, var_dict, curr_list, missing_var[1:], var_index)
            else:
                for val in var_dict[next_var]:
                    index = var_index[next_var]
                    if isinstance(index, list):
                        for curr_index in index:
                            curr_list[curr_index] = val
                    else:
                        curr_list[var_index[next_var]] = val
                    Utils._substitute_var_rec(solutions, var_dict, curr_list, missing_var[1:], var_index)


    @staticmethod
    def _substitute_var_rec(solutions, var_dict, curr_list, missing_var, var_index):
        """
        Funzione di supporto per poter effettuare la sostituzione delle variabili
        con i loro rispettivi valori
        @param solutions lista di combinazioni corrette generate
        @param var_dict valori da associare alle variabili
        @param curr_list combinazione che si sta generando
        @param missing_var variabili non ancora ispezionate
        @param var_index posizione nel pattern delle variabili
        """
        if not Utils.has_variable(curr_list):
            solutions.append(curr_list[:])
        else:
            next_var = missing_var[0]
            if isinstance(missing_var[0], list):  #template
                for val in var_dict[next_var[1]]:
                    index = var_index[next_var[1]]
                    if isinstance(index, list):
                        for curr_index in index:
                            curr_list[curr_index] = val
                    else:
                        curr_list[var_index[next_var[1]]] = [next_var[0], val]
                    Utils._substitute_var_rec(solutions, var_dict, curr_list, missing_var[1:], var_index)
            else:
                for val in var_dict[next_var]:
                    index = var_index[next_var]
                    if isinstance(index, list):
                        for curr_index in index:
                            curr_list[curr_index] = val
                    else:
                        curr_list[var_index[next_var]] = val
                    Utils._substitute_var_rec(solutions, var_dict, curr_list, missing_var[1:], var_index)


    @staticmethod
    def substitute_variable(fact, var_dict):
        """
        Sostituisce le variabili con i loro effettivi valori
        @param fact fatto con le variabili da sostituire
        @param var_dict mapping tra le variabili ed i loro possibili valori
        """

        pattern = fact[1:]
        variables = []

        for x in pattern:
            if (isinstance(x, list) and x[1].startswith('?')) or x.startswith('?'):
                variables.append(x)

        if len(variables) > 1: # different variables in fact
            first_variable = variables[0]
            all_solutions = []

            var_index = {}
            for i in range(len(pattern)):
                if isinstance(pattern[i], list):
                    if pattern[i][1] in var_index:
                        if isinstance(var_index[pattern[i]], list):
                            var_index[pattern[i][1]].append(i)
                        else:
                            var_index[pattern[i][1]] = [var_index[pattern[i][1]], i]
                    else:
                        var_index[pattern[i][1]] = i
                elif pattern[i].startswith('?'):
                    if pattern[i] in var_index:
                        if isinstance(var_index[pattern[i]], list):
                            var_index[pattern[i]].append(i)
                        else:
                            var_index[pattern[i]] = [var_index[pattern[i]], i]
                    else:
                        var_index[pattern[i]] = i

            curr_list = pattern[:]

            if isinstance(first_variable, list): #template
                for val in var_dict[first_variable[1]]:  # costruisco l'albero a partire dai valori assunti dalla prima variabile
                    index = var_index[first_variable[1]]
                    if isinstance(index, list):
                        for curr_index in index:
                            curr_list[curr_index] = val
                        var_index[first_variable[1]] = index[1:]
                    else:
                        curr_list[var_index[first_variable[1]]] = [first_variable[0], val]
                    Utils._substitute_var_rec(all_solutions, var_dict, curr_list, variables[1:], var_index)
                    var_index[first_variable[1]] = index
                    curr_list = pattern[:]
            else:
                for val in var_dict[first_variable]:  # costruisco l'albero a partire dai valori assunti dalla prima variabile
                    index = var_index[first_variable]
                    if isinstance(index, list):
                        for curr_index in index:
                            curr_list[curr_index] = val
                        var_index[first_variable] = index[1:]
                    else:
                        curr_list[var_index[first_variable]] = val
                    Utils._substitute_var_rec(all_solutions, var_dict, curr_list, variables[1:], var_index)
                    var_index[first_variable] = index
                    curr_list = pattern[:]

            return all_solutions
        else:
            solutions = []
            var_index = list(pattern).index(variables[0])

            if isinstance(variables[0], list):
                for val in var_dict[variables[0][1]]:
                    solutions.append([pattern[i] if i != var_index else [variables[0][0], val] for i in range(len(pattern))])
            else:
                for val in var_dict[variables[0]]:
                    solutions.append([pattern[i] if i != var_index else val for i in range(len(pattern))])

            return solutions

    @staticmethod
    def capture_variables_id(condition):
        var_index = []
        condition_len = len(condition)
        i = 0

        while i < condition_len:
            if condition[i] == '?':
                split = condition[i:]
                try:
                    space_index = i + split.index(' ')
                    var_index.append(condition[i:space_index])
                except ValueError:
                    var_index.append(condition[i:condition_len-1])

                var_index[-1] = str(var_index[-1]).strip(')')
                i += len(var_index[-1])
            i += 1
        return var_index

    @staticmethod
    def substitute_variable_string(original, var_dict):
        """
        Provvede a generare tutte le possibili stringhe a partire da un determinato
        pattern che coinvolge delle variabili, avendo a disposizione i possibili
        valori associabili alle stesse
        @param original: pattern da utilizzare per la generazioni delle combinazioni
        @param var_dict: dizionario avente come chiava l'identificativo di una variabile
        e come valore una lista di possibili valori ad essa associati
        """

        solutions = []
        variable_list = Utils.capture_variables_id(original) # salva in ordine di occorrenza tutte le variabili

        # fissa la prima variabile e fai scorrere tutte le altre
        for var_value in var_dict[variable_list[0]]:
            # rimpiazza tutte le occorrenze della prima variabile
            # con il valore che attualmente assume
            curr_sol = original.replace(variable_list[0], var_value)
            # chiama ricorsivamente la funzione di sostituzione per poter
            # sostituire le restanti variabili
            Utils._substitute_variable_string_rec(var_dict, curr_sol, variable_list[1:], solutions)

        return solutions

    @staticmethod
    def _substitute_variable_string_rec(var_dict, curr_sol, missing_var, solutions):
        """
        Provvede a generare tutte le possibili stringhe a partire da un determinato
        pattern che coinvolge delle variabili, avendo a disposizione i possibili
        valori associabili alle stesse.

        Tale funzione funge da supporto per la generazione delle differenti combinazioni,
        in quanto rappresenta il passo ricorsivo nel quale viene fissato il valore della variabile
        che precede quella corrente nel pattern.

        @param original: pattern da utilizzare per la generazioni delle combinazioni
        @param var_dict: dizionario avente come chiava l'identificativo di una variabile
        e come valore una lista di possibili valori ad essa associati
        """
        if not missing_var:
            solutions.append(curr_sol)
        else:
            # acquisisci la prossima variabile da sostituire
            next_var = missing_var[0]

            # per ogni singolo valore della variabile corrente
            for var_value in var_dict[next_var]:
                # rimpiazza ogni occorrenza della variabile corrente con il valore corrente
                curr_sol_gen = curr_sol.replace(next_var, var_value)
                # genera ricorsivamente la soluzione
                Utils._substitute_variable_string_rec(var_dict, curr_sol_gen, missing_var[1:], solutions)


    @staticmethod
    def is_boolean_expr(cond_list):
        assert isinstance(cond_list, str)

        if '<' in cond_list\
            or '>' in cond_list\
            or '<=' in cond_list\
            or '>=' in cond_list\
            or '==' in cond_list\
            or '!=' in cond_list:
            return True

        return False
