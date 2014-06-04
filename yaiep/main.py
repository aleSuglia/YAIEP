from pyparsing import Keyword, Literal, Word, nums, Combine, alphas, OneOrMore, Group
from yaiep.core.InferenceEngine import InferenceEngine
from yaiep.core.UIManager import UIManager
from yaiep.grammar.YAIEPGrammar import YAIEPGrammar
from yaiep.interpreter.Interpreter import Interpreter
from yaiep.ml import KnowledgeAcquisition


if __name__ == '__main__':
    inter = Interpreter()
    inter.start()

