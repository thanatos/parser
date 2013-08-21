==================================
A library about parsing for Python
==================================

This library is about grammars and parsing, and in particular, `LR parsers`_.

State
-----
Currently, the library has the capability to describe a grammar, and derive the
transitions between item sets (parser states) of that grammar. It cannot (yet)
build the actual parser. (The transition table needs to be convert to action
and goto tables, and an engine capable of using those tables needs to be
written.) See the Wikipedia article `LR parsers`_ sections on “`Constructing
LR(0) parsing tables`_” and “`Table construction`_” — the code is currently at
the step “`Constructing the action and goto tables`_”.

.. _LR parsers: https://en.wikipedia.org/wiki/LR_parser
.. _Constructing LR(0) parsing tables: https://en.wikipedia.org/wiki/LR_parser#Constructing_LR.280.29_parsing_tables
.. _Table construction: https://en.wikipedia.org/wiki/LR_parser#Table_construction
.. _Constructing the action and goto tables: https://en.wikipedia.org/wiki/LR_parser#Constructing_the_action_and_goto_tables
