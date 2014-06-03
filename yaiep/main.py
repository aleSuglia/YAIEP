from pyparsing import Keyword, Literal, Word, nums, Combine, alphas, OneOrMore, Group
from yaiep.core.InferenceEngine import InferenceEngine
from yaiep.core.UIManager import UIManager
from yaiep.grammar.YAIEPGrammar import YAIEPGrammar
from yaiep.interpreter.Interpreter import Interpreter
from yaiep.ml import KnowledgeAcquisition


if __name__ == '__main__':
    # inter = Interpreter()
    #    inter.start()
    grammar = YAIEPGrammar().get_grammar_definition()
    print(grammar.parseFile('conf_file', parseAll=True))
    #  engine = InferenceEngine()
    #  engine.load_engine('games/secchi/settings', 'games/secchi/conf_file')
   #engine.load_engine('rule_file')
#   engine.solve_problem()
#    print(engine)
#    list_rules = {}

#    KnowledgeAcquisition.knowledge_acquisition(list_rules, 'knowledge/tennis.arff')
#    print(list_rules)

