from yaiep.interpreter.Interpreter import Interpreter

##
# @mainpage Progetto di Ingegneria della Conoscenza e Sistemi Esperti a.a. 2013-2014
#
# @section Introduzione
# Nel corso degli anni nel campo dell'intelligenza artificiale vennero proposte diverse soluzioni per la simulazione del pensiero umano.
# Una in particolare fu proposta da Allen Newell che teorizzò uno dei primissimi esempi di quelli che oggi sono definiti sistemi a produzione
# (production systems) ovvero, particolari modello di calcolo che si basavano su delle regole. Queste regole erano costituite da una parte sinistra
# e da una parte destra, la prima presentava delle # condizioni che dovevano essere necessariamente soddisfatte per poter garantire l'attivazione e
# l'esecuzione delle azioni nella corrispondente parte destra.
# Tale metodologia di calcolo differiva enormemente rispetto a quella largamente adottata in quegli anni, nella quale, si dava molta più importanza
# alla modalità di risoluzione dei problemi secondo un approccio algoritmico ben definito.
# La staticità e la presenza di un percorso ben preciso che fosse in grado di definire esattamente l'obiettivo da raggiungere
# non era sufficiente per poter risolvere i problemi che in quel periodo erano oggetto di studio da parte dei ricercatori del
# campo dell'intelligenza artificiale. La potenzialità dei sistemi a produzione risiedeva nella loro capacità di agire
# e muoversi in maniera tentativa (euristica) all'interno dello spazio delle soluzioni, mediante un insieme di regole che davano
# la possibilità al sistema di transitare in uno stato ritenuto stato goal o stato obiettivo per il problema in analisi.
#


if __name__ == '__main__':
    inter = Interpreter()
    inter.start()

