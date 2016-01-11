YAIEP: Yet Another Inference Engine in Python
=====

A simple inference engine written entirely in Python3 which uses as a reasoning mechanism **forward-chaining**. 

It's able to load a knowledge base written using a CLIPS-like grammar. The knowledge base is composed by facts and rules. Optionally, it is able to define goals that the system should reach during the *recognize-act* cycle.

It implements a simple interpreter which allows the user to choose the specific knowledge base that he wants to load and let him querying the knowledge base.

As an extension, it supports  [C5.0](https://www.rulequest.com/see5-info.html), a decision tree toolkit, which allow the system to learn from a specific dataset a set of rules which are automatically loaded in the knowledge base.

