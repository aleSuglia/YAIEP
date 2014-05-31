from pyparsing import Word, Literal, OneOrMore, alphas, nums, Optional, Group, ZeroOrMore, Forward, Keyword, Dict, \
    operatorPrecedence, opAssoc, oneOf, originalTextFor, Combine
from yaiep.grammar.Grammar import Grammar


# ##
# Classe che presenta la definizione della grammatica attualmente adoperata
# per poter scrivere il file di configurazione da dare in pasto al motore di inferenza
# per poter avviare la risoluzione di un determinato problema
class YAIEPGrammar(Grammar):
    __keyword_list = ['globals', 'template', 'facts', 'rule', 'final_state']

    def get_keyword_list(self):
        return YAIEPGrammar.__keyword_list

    def get_grammar_definition(self):
        op = Literal('and') | Literal('or') | Literal('bind')
        function_mono = Keyword('abs')

        logicOperator = Literal('==') | Literal('!=') | Literal('<=') | Literal('>=') | Literal('<') | Literal('>')
        lpar = Literal('(').suppress()
        rpar = Literal(')').suppress()
        integer = Word(nums)
        global_variable_invocation = Combine(Keyword('global') + Literal('.') + Literal('?') + Word(alphas + '_-'))
        variable = Word('?', alphas + '_-') | global_variable_invocation

        operand = variable | integer
        multop = oneOf('* /')
        plusop = oneOf('+ -')

        global_var_definition = Group(lpar + variable + (Word(alphas) | Word(nums)) + rpar)
        globals_definition = lpar + Keyword('globals') + OneOrMore(global_var_definition) + rpar

        arithExpr = operatorPrecedence(operand,
                                       [(multop, 2, opAssoc.LEFT),
                                        (plusop, 2, opAssoc.LEFT)]
        )

        arith_function_mono = function_mono + lpar + (arithExpr | Word(nums)) + rpar

        logicalExpr = originalTextFor(lpar + (Word(nums) | arithExpr | variable | arith_function_mono) + logicOperator + \
                                      (Word(nums) | arithExpr | variable | arith_function_mono) + rpar)

        identifier = Word(alphas + "_-")
        parameters = variable | originalTextFor(arith_function_mono) | Word(alphas + "_") | integer | originalTextFor(
            arithExpr)

        single_slot = Group(lpar + identifier + parameters + rpar)

        fact = Group(lpar + identifier + (OneOrMore(parameters) | OneOrMore(single_slot)) + rpar)
        facts = lpar + Literal('facts').suppress() + OneOrMore(fact) + rpar
        facts_list = OneOrMore(facts)

        #func_param = parameters | fact
        #function = Group(lpar + op + func_param + func_param + rpar)

        function = Group(lpar + op + variable + fact + rpar)

        cond_attr = fact | function
        condition_attributes = OneOrMore(cond_attr)

        assertAction = Forward()
        atomAssertAction = Keyword("assert") + OneOrMore(fact) | Group(lpar + assertAction + rpar)
        assertAction << atomAssertAction + ZeroOrMore(assertAction)

        modifyAction = Forward()
        atomModifyAction = Keyword("modify") + (Word(nums) | variable) + Group(OneOrMore(single_slot)) | \
                           Group(lpar + modifyAction + rpar)
        modifyAction << atomModifyAction + ZeroOrMore(modifyAction)

        action = assertAction | modifyAction

        salience_param = lpar + Keyword('salience') + Word(nums) + rpar

        rule = Group(
            Group(lpar + Keyword('rule').suppress() + Optional(salience_param) + condition_attributes + ZeroOrMore(
                logicalExpr))
            + Keyword("then").suppress() + Group(OneOrMore(action)) + rpar)

        # original rule
        #rule = Group(
        #    Group(lpar + Keyword('rule').suppress() + condition_attributes) + Keyword("then").suppress() + Group(
        #        OneOrMore(action)) + rpar)

        rule_list = OneOrMore(rule)

        final_state = lpar + Keyword('final_state').suppress() + fact + rpar

        single_slot_specifier = Group(
            lpar + Keyword('default') + (integer | global_variable_invocation | Word(alphas)) + rpar) | \
                                Group(lpar + Keyword('type') + (Literal('string') | Literal('integer')) + rpar)

        double_slot_specifier = Group(lpar + Keyword('range') + integer + integer + rpar | \
                                      lpar + Keyword('range') + integer + global_variable_invocation + rpar | \
                                      lpar + Keyword('range') + global_variable_invocation + integer + rpar | \
                                      lpar + Keyword(
                                          'range') + global_variable_invocation + global_variable_invocation + rpar)

        slot_specifier = single_slot_specifier | double_slot_specifier

        slot = lpar + Keyword('slot').suppress() + identifier + rpar | Group(lpar + Keyword('slot').suppress()
                                                                             + identifier + ZeroOrMore(
            slot_specifier) + rpar)
        def_template = Group(lpar + Keyword('template').suppress() + identifier + OneOrMore(slot) + rpar)
        list_template = OneOrMore(def_template)

        return Dict(Optional(globals_definition.setParseAction(lambda s: ('globals', s.asList()))) + \
                    Optional(list_template.setParseAction(lambda s: ('template', s.asList()))) + \
                    Optional(facts_list.setParseAction(lambda s: ('facts', s.asList()))) + \
                    Optional(rule_list.setParseAction(lambda s: ('rule', s.asList()))) + \
                    Optional(final_state.setParseAction(lambda s: ('final_state', s.asList()))))
