# coding: utf-8
import itertools
import unittest

import lr_parser


class LrParserTest(unittest.TestCase):
    def _create_grammar(self):
        # The small grammar from Wikipedia.
        gE = lr_parser.NonTerminal('E')
        gStar = lr_parser.Terminal('*')
        gB = lr_parser.NonTerminal('B')
        gPlus = lr_parser.Terminal('+')
        gZero = lr_parser.Terminal('0')
        gOne = lr_parser.Terminal('1')

        self.gE = gE
        self.gStar = gStar
        self.gB = gB
        self.gPlus = gPlus
        self.gZero = gZero
        self.gOne = gOne

        self.rules = [
            (gE, (gE, gStar, gB)),
            (gE, (gE, gPlus, gB)),
            (gE, (gB,)),
            (gB, (gZero,)),
            (gB, (gOne,)),
        ]
        self.rules = list(
            itertools.starmap(lr_parser.Production, self.rules))

        self.grammar = lr_parser.Grammar(self.rules, gE)

    def test_create_grammar(self):
        self._create_grammar()

        productions = self.grammar.productions_of(self.gE)
        self.assertCountEqual(
            [
                lr_parser.Production(self.gE, (self.gE, self.gStar, self.gB)),
                lr_parser.Production(self.gE, (self.gE, self.gPlus, self.gB)),
                lr_parser.Production(self.gE, (self.gB,)),
            ],
            productions)

    def test_production(self):
        self._create_grammar()

        gE = self.gE
        gStar = self.gStar
        gB = self.gB
        production1 = lr_parser.Production(gE, (gE, gStar, gB))
        production2 = lr_parser.Production(gE, (gE, gStar, gB))
        self.assertIsNot(production1, production2)
        self.assertEqual(production1, production2)
        self.assertEqual(hash(production1), hash(production2))

    def test_item(self):
        self._create_grammar()

        gE = self.gE
        gStar = self.gStar
        gB = self.gB
        production = lr_parser.Production(gE, (gE, gStar, gB))
        item = lr_parser.Item(production, 2)
        self.assertEqual(gB, item.expecting_symbol)

        item = item.advance()
        self.assertEqual(3, item.parse_position)
        self.assertEqual(None, item.expecting_symbol)

        with self.assertRaises(ValueError) as cm:
            item.advance()
        self.assertRegex(
            cm.exception.args[0],
            'Can\'t advance item:'
            ' Parser position already at end of production.')

    def test_item_str(self):
        self._create_grammar()

        gE = self.gE
        gStar = self.gStar
        gB = self.gB
        production = lr_parser.Production(gE, (gE, gStar, gB))
        item = lr_parser.Item(production, 2)
        # Just check that it doesn't raise.
        str(item)

    def test_closure(self):
        self._create_grammar()

        itemset = (lr_parser.Item(self.rules[0], 0),)

        closed_itemset = lr_parser.closure(itemset, self.grammar)

        expected_itemset = [lr_parser.Item(rule, 0) for rule in self.rules]
        # Even if they're all wrong, it's okay.
        self.maxDiff = None
        self.assertCountEqual(expected_itemset, closed_itemset)

    def test_construct_transition(self):
        self._create_grammar()

        closed_item_set = lr_parser.closure(
            (lr_parser.Item(self.grammar.starting_production, 0),),
            self.grammar)

        transitions = lr_parser.construct_transition(
            closed_item_set, self.grammar)

        Item = lr_parser.Item
        Production = lr_parser.Production

        expected_output = {
            self.gZero: {
                Item(Production(self.gB, (self.gZero,)), 1),
            },
            self.gOne: {
                Item(Production(self.gB, (self.gOne,)), 1),
            },
            self.gE: {
                Item(self.grammar.starting_production, 1),
                Item(Production(self.gE, (self.gE, self.gStar, self.gB)), 1),
                Item(Production(self.gE, (self.gE, self.gPlus, self.gB)), 1),
            },
            self.gB: {
                Item(Production(self.gE, (self.gB,)), 1),
            }
        }
        self.maxDiff = None
        self.assertEqual(expected_output, transitions)

    def test_construct_all_transitions(self):
        self._create_grammar()
        output = lr_parser.construct_all_transitions(self.grammar)
        for item_set, transitions in output.items():
            print('Item set:')
            for item in item_set:
                print(item)
        import pprint
        pprint.pprint(output)


if __name__ == '__main__':
    unittest.main()
