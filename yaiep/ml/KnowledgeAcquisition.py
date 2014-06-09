import csv
import os
from subprocess import DEVNULL
import numpy
from yaiep.ml.C5RuleParser import C5RuleParser
from scipy.io import arff
from yaiep.ml.KAException import KAException

knowledge_path = "knowledge" + os.sep


# #
# Funzione che provvede ad avviare il processo di apprendimento automatico
# delle regole a partire da un dataset in formato .arff (http://www.cs.waikato.ac.nz/ml/weka/arff.html)
# mediante il tool di creazione di alberi di decisione C5 (http://www.rulequest.com/see5-info.html).
# Tale tool una volta avviato genera un albero di decisione a partire dal quale vengono opportunamente
# generate delle regole che vengono importate nel motore inferenziale.
#
# E' necessario che il file contente il dataset da utilizzare sia presente nella cartella "knowledge"
# del programma e che sia formattato secondo la sintassi del formato ARFF.
#
# @param list_rules: lista di regole da generare
# @param dataset_filename: nome del dataset in formato .arff
#
def knowledge_acquisition(list_rules, dataset_filename):
    try:
        with open(dataset_filename) as dataset:
            dataset_arff, meta_information = arff.loadarff(dataset)
            filesystem_name = dataset_filename[dataset_filename.rfind(os.sep)+1:len(dataset_filename)-5]
            rules_file = knowledge_path + filesystem_name + ".rules"
            names_file = knowledge_path + filesystem_name + ".names"
            data_file = knowledge_path + filesystem_name + ".data"
            _print_names_file(meta_information, names_file)
            _print_data_file(dataset_arff, data_file)
            import subprocess
            subprocess.call("cd knowledge; c5.0 -f " + filesystem_name + " -r", shell=True, stdout=DEVNULL)
            new_rules = C5RuleParser().get_rules(rules_file, names_file)
            list_rules.extend(new_rules)
    except Exception as ex:
        raise KAException('Unable to read load dataset')


# #
# Genera il file che conterrà i nomi degli attributi presenti all'interno del dataset specificato
# secondo il formato specificato richiesto dal tool di generazione degli alberi di decisione.
#
# @param meta_information: informazioni relative agli attributi presenti nel dataset
# @param names_filename: nome del file nel quale verranno memorizzati i nomi degli attributi
#
def _print_names_file(meta_information, names_filename):
    with open(names_filename, mode='w') as names_file:
        # Memorizza il nome dell'attributo di classe
        class_attribute_name = meta_information._attrnames[-1]
        names_file.write('{0}.\n'.format(class_attribute_name))

        for attribute in meta_information._attrnames:
            names_file.write('{0}: '.format(attribute))
            if meta_information._attributes[attribute][0] != 'numeric':
                attributes_values = meta_information._attributes[attribute][1]
                len_attributes_values = len(attributes_values)
                for i, val in enumerate(attributes_values):
                    if i != len_attributes_values-1:
                        names_file.write(val + ', ')
                    else:
                        names_file.write(val + '.\n')
            else:
                names_file.write('continuous.\n')


# #
# Genera il file che conterrà i dati del dataset che verranno adoperato per poter
# generare l'albero di decisione
# @param data: tuple del dataset
# @param data_filename: nome del file nel quale verranno memorizzate le tuple del dataset
def _print_data_file(data, data_filename):
    with open(data_filename, mode='w') as data_file:
        for tuple in data:
            len_tuple = len(tuple)
            for i, val in enumerate(tuple):
                if isinstance(val, numpy.float64):
                    str_val = str(val)
                else:
                    str_val = val.decode(encoding='UTF-8')
                if i != len_tuple-1:
                    data_file.write(str_val + ',')
                else:
                    data_file.write(str_val + '\n')