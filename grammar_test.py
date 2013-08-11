# coding: utf-8
import unittest

import grammar


class TerminalNonTerminalTest(unittest.TestCase):
    def test_terminal(self):
        class_literal = grammar.Terminal('class')
        self.assertEqual('class', class_literal.name)

        t_a = grammar.Terminal('A "test" literal')
        self.assertEqual('"A ""test"" literal"', str(t_a))
        self.assertEqual('<Terminal "A ""test"" literal">', repr(t_a))

        t_b = grammar.Terminal('weird?', is_literal=False)
        self.assertEqual('?weird???', str(t_b))
        self.assertEqual('<Terminal ?weird???>', repr(t_b))

    def test_non_terminal(self):
        a_non_terminal = grammar.NonTerminal('expr')
        self.assertEqual('expr', a_non_terminal.name)
        self.assertEqual('<expr>', str(a_non_terminal))
        self.assertEqual('<NonTerminal <expr>>', repr(a_non_terminal))


class ProductionTest(unittest.TestCase):
    def setUp(self):
        self.simple_expr = grammar.NonTerminal('expr')
        self.a_number = grammar.Terminal('number', is_literal=False)
        self.a_plus = grammar.Terminal('+')
        self.a_production = grammar.Production(
            self.simple_expr, [self.a_number, self.a_plus, self.simple_expr])

    def test_production(self):
        self.assertEqual(self.simple_expr, self.a_production.non_terminal)
        self.assertSequenceEqual(
            [self.a_number, self.a_plus, self.simple_expr],
            self.a_production.produces)

    def test_str(self):
        self.assertEqual(
            '<expr> ::= ?number? "+" <expr>', str(self.a_production))

    def test_repr(self):
        self.assertEqual(
            'grammar.Production(<NonTerminal <expr>>,'
            ' (<Terminal ?number?>, <Terminal "+">, <NonTerminal <expr>>))',
            repr(self.a_production))

    def test_eq_and_hash(self):
        same_production = grammar.Production(
            self.simple_expr, [self.a_number, self.a_plus, self.simple_expr])
        different_production = grammar.Production(
            self.simple_expr, [self.a_number, self.a_plus, self.a_number])
        self.assertEqual(self.a_production, same_production)
        self.assertNotEqual(same_production, different_production)
        self.assertEqual(hash(self.a_production), hash(same_production))


if __name__ == '__main__':
    unittest.main()
