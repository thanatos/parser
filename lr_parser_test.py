# coding: utf-8
import itertools
import unittest

import grammar
import lr_parser


def _create_grammar():
    # Create the simple grammar from Wikipedia:
    # (http://en.wikipedia.org/wiki/LR_parser#Additional_Example_1.2B1)
    class WikipediaGrammar(object):
        ZERO = grammar.Terminal('0')
        ONE = grammar.Terminal('1')
        PLUS = grammar.Terminal('+')
        STAR = grammar.Terminal('*')

        B = grammar.NonTerminal('B')
        E = grammar.NonTerminal('E')

        PRODUCTIONS = [
            (E, (E, STAR, B)),
            (E, (E, PLUS, B)),
            (E, (B,)),
            (B, (ZERO,)),
            (B, (ONE,)),
        ]
        PRODUCTIONS = list(itertools.starmap(grammar.Production, PRODUCTIONS))
        PRODUCTION_E_E_STAR_B = PRODUCTIONS[0]
        PRODUCTION_E_E_PLUS_B = PRODUCTIONS[1]
        PRODUCTION_E_B = PRODUCTIONS[2]

    return WikipediaGrammar


class ItemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(ItemTest, cls).setUpClass()
        cls.grammar = _create_grammar()

    @classmethod
    def _create_item(cls):
        return lr_parser.Item(cls.grammar.PRODUCTION_E_E_STAR_B, 1)

    def test_attrs(self):
        item = lr_parser.Item(self.grammar.PRODUCTION_E_E_STAR_B, 1)
        # .production
        self.assertEqual(self.grammar.PRODUCTION_E_E_STAR_B, item.production)
        self.assertEqual(1, item.parse_position)
        # .expecting_symbol
        self.assertEqual(self.grammar.STAR, item.expecting_symbol)

    def test_eq_and_hash(self):
        item_a = self._create_item()
        item_b = self._create_item()
        self.assertEqual(item_a, item_b)
        self.assertEqual(hash(item_a), hash(item_b))
        item_c = item_b.advance()
        self.assertNotEqual(item_a, item_c)

    def test_repr(self):
        item = self._create_item()
        self.assertRegex(
            repr(item),
            '^Item\\(grammar.Production\\(.*\\), 1\\)$')

    def test_str(self):
        item = self._create_item()
        self.assertEqual('<E> ::= <E> @ "*" <B>', str(item))

    def test_advance(self):
        item_a = self._create_item()
        self.assertEqual(1, item_a.parse_position)
        item_b = item_a.advance()
        self.assertEqual(2, item_b.parse_position)
        self.assertEqual(item_a.production, item_b.production)

        item_c = item_b.advance()
        # Item C is E → E * B•, and thus can't be advanced further.
        with self.assertRaises(ValueError):
            item_c.advance()


class GrammarTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(GrammarTest, cls).setUpClass()
        cls.GRAMMAR = _create_grammar()

    def test_grammar(self):
        augmented_grammar = lr_parser.Grammar(
            self.GRAMMAR.PRODUCTIONS, self.GRAMMAR.E)
        self.assertIsInstance(
            augmented_grammar.starting_symbol, grammar.NonTerminal)
        self.assertIsInstance(
            augmented_grammar.starting_production, grammar.Production)
        self.assertEqual(
            augmented_grammar.starting_production.non_terminal,
            augmented_grammar.starting_symbol)
        self.assertEqual(
            (self.GRAMMAR.E,), augmented_grammar.starting_production.produces)

        self.assertCountEqual(
            [
                self.GRAMMAR.PRODUCTION_E_E_STAR_B,
                self.GRAMMAR.PRODUCTION_E_E_PLUS_B,
                self.GRAMMAR.PRODUCTION_E_B,
            ],
            augmented_grammar.productions_of(self.GRAMMAR.E))


class LrParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.GRAMMAR = _create_grammar()

    def test_closure(self):
        itemset = (lr_parser.Item(self.GRAMMAR.PRODUCTION_E_E_STAR_B, 0),)

        augmented_grammar = lr_parser.Grammar(
            self.GRAMMAR.PRODUCTIONS, self.GRAMMAR.E)
        closed_itemset = lr_parser.closure(itemset, augmented_grammar)

        expected_itemset = [
            lr_parser.Item(production, 0)
            for production in self.GRAMMAR.PRODUCTIONS]
        # Even if they're all wrong, it's okay.
        self.maxDiff = None
        self.assertCountEqual(expected_itemset, closed_itemset)

    def test_construct_transition(self):
        augmented_grammar = lr_parser.Grammar(
            self.GRAMMAR.PRODUCTIONS, self.GRAMMAR.E)
        # Start with Just the item S → •E. Closing this,
        closed_item_set = lr_parser.closure(
            (lr_parser.Item(augmented_grammar.starting_production, 0),),
            augmented_grammar)
        # we get the item set:
        # S → •E
        # E → •E * B
        # E → •E + B
        # E → •B
        # E → •0
        # E → •1

        # Now we construct the transitions. If we move some symbol X, what
        # state (item set) is the parser now in?
        transitions = lr_parser.construct_transition(
            closed_item_set, augmented_grammar)

        Item = lr_parser.Item
        Production = grammar.Production
        g = self.GRAMMAR

        # The output from construct_transition maps the symbol we
        # consumed/parsed to the new state (or item set) we will be in.
        expected_output = {
            g.ZERO: {
                Item(Production(g.B, (g.ZERO,)), 1),
            },
            g.ONE: {
                Item(Production(g.B, (g.ONE,)), 1),
            },
            g.E: {
                Item(augmented_grammar.starting_production, 1),
                Item(Production(g.E, (g.E, g.STAR, g.B)), 1),
                Item(Production(g.E, (g.E, g.PLUS, g.B)), 1),
            },
            g.B: {
                Item(Production(g.E, (g.B,)), 1),
            }
        }
        self.maxDiff = None
        self.assertEqual(expected_output, transitions)

    def test_construct_all_transitions(self):
        # Very similar to construct_transition, except we explore all possible
        # transitions, instead of just a single step.
        augmented_grammar = lr_parser.Grammar(
            self.GRAMMAR.PRODUCTIONS, self.GRAMMAR.E)

        transitions = lr_parser.construct_all_transitions(augmented_grammar)

        Item = lr_parser.Item
        Production = grammar.Production
        g = self.GRAMMAR

        # The output maps an item set to a transition table. The transition
        # table itself is a mapping from "consumed symbol" to new itemset.
        # We're going to name the item sets to make managing this (rather
        # large) output simpler.
        state_large_start = frozenset({
            Item(augmented_grammar.starting_production, 0),
            Item(Production(g.E, (g.E, g.STAR, g.B)), 0),
            Item(Production(g.E, (g.E, g.PLUS, g.B)), 0),
            Item(Production(g.E, (g.B,)), 0),
            Item(Production(g.B, (g.ZERO,)), 0),
            Item(Production(g.B, (g.ONE,)), 0),
        })
        state_finish_zero = frozenset({
            Item(Production(g.B, (g.ZERO,)), 1),
        })
        state_finish_one = frozenset({
            Item(Production(g.B, (g.ONE,)), 1),
        })
        state_finish_e = frozenset({
            Item(augmented_grammar.starting_production, 1),
            Item(Production(g.E, (g.E, g.STAR, g.B)), 1),
            Item(Production(g.E, (g.E, g.PLUS, g.B)), 1),
        })
        state_finish_b = frozenset({
            Item(Production(g.E, (g.B,)), 1),
        })
        state_finish_star = frozenset({
            Item(Production(g.E, (g.E, g.STAR, g.B)), 2),
            Item(Production(g.B, (g.ZERO,)), 0),
            Item(Production(g.B, (g.ONE,)), 0),
        })
        state_finish_plus = frozenset({
            Item(Production(g.E, (g.E, g.PLUS, g.B)), 2),
            Item(Production(g.B, (g.ZERO,)), 0),
            Item(Production(g.B, (g.ONE,)), 0),
        })
        state_finish_e_star_b = frozenset({
            Item(Production(g.E, (g.E, g.STAR, g.B)), 3),
        })
        state_finish_e_plus_b = frozenset({
            Item(Production(g.E, (g.E, g.PLUS, g.B)), 3),
        })

        expected_output = {
            state_large_start: {
                g.ZERO: state_finish_zero,
                g.ONE: state_finish_one,
                g.E: state_finish_e,
                g.B: state_finish_b,
            },
            state_finish_zero: {},
            state_finish_one: {},
            state_finish_e: {
                g.STAR: state_finish_star,
                g.PLUS: state_finish_plus,
            },
            state_finish_b: {},
            state_finish_star: {
                g.ZERO: state_finish_zero,
                g.ONE: state_finish_one,
                g.B: state_finish_e_star_b,
            },
            state_finish_plus: {
                g.ZERO: state_finish_zero,
                g.ONE: state_finish_one,
                g.B: state_finish_e_plus_b,
            },
            state_finish_e_star_b: {},
            state_finish_e_plus_b: {},
        }
        self.maxDiff = None
        self.assertEqual(expected_output, transitions)


if __name__ == '__main__':
    unittest.main()
