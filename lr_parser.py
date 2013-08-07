"""LR parser generator."""

import collections

import grammar as _grammar


class Item(object):
    def __init__(self, rule, parse_position):
        self.rule = rule
        self.parse_position = parse_position

    def __eq__(self, other):
        return (self.rule == other.rule
                and self.parse_position == other.parse_position)

    def __hash__(self):
        return hash((self.rule, self.parse_position))

    def __repr__(self):
        return 'Item({0!r}), {1!r})'.format(self.rule, self.parse_position)

    def __str__(self):
        before_point = self.rule.produces[:self.parse_position]
        after_point = self.rule.produces[self.parse_position:]
        produce_str = []
        produce_str.extend(str(s) for s in before_point)
        produce_str.append('@')
        produce_str.extend(str(s) for s in after_point)
        produce_str = ' '.join(produce_str)

        return '{0} -> {1}'.format(
            self.rule.non_terminal,
            produce_str)

    @property
    def expecting_symbol(self):
        if self.parse_position >= len(self.rule.produces):
            return None
        return self.rule.produces[self.parse_position]

    def advance(self):
        if self.parse_position >= len(self.rule.produces):
            raise ValueError(
                'Can\'t advance item: Parser position already at end of'
                ' production.')
        return Item(self.rule, self.parse_position + 1)


class Grammar(object):
    """The grammar of a language.

    Note that internally, a new non-terminal will be created ("S"), such
    that S → starting_symbol, to help the parser determine when it has
    accepted input.

    :param rules: The productions of the grammar.
    :type rules: iterable of Production objects
    :param starting_symbol: The "starting" symbol of the grammar. The
        represents a state at which the parser may conclude parsing, and
        have parse tree which is a valid parse of the grammar.
    :type starting_symbol: NonTerminal
    """

    def __init__(self, productions, starting_symbol):
        self._indexed_productions = {}
        for production in productions:
            self._indexed_productions.setdefault(
                    production.non_terminal, []).append(production)

        self._starting_symbol = _grammar.NonTerminal('S')
        self._starting_production = _grammar.Production(
                self._starting_symbol, [starting_symbol])
        self._indexed_productions[self._starting_symbol] = (
            self._starting_production)

    @property
    def starting_symbol(self):
        return self._starting_symbol

    @property
    def starting_production(self):
        return self._starting_production

    def productions_of(self, non_terminal):
        return self._indexed_productions[non_terminal]


def closure(item_set, grammar):
    """Return the closure of an item set.

    The closure of an item set is the item set where any items with the parse
    position at a non-terminal have any corresponding production rules for that
    non-terminal in the item set as well.

    E.g., if we have the item:

      A → B •C D

    …where the • represents the parse position, and if C is:

      C → E F G

    Then we include

      C → •E F G

    …in the item set. (And repeat this process, if the newly added item has the
    parse position in front of a non-terminal.)

    :param item_set: The item set to close.
    :param grammar: A mapping of non-terminals to productions.
    :returns: The closed item set.
    """
    item_set = set(item_set)
    queue = collections.deque(item_set)

    while queue:
        item = queue.popleft()
        parser_expecting_symbol = item.expecting_symbol
        if parser_expecting_symbol is None:
            continue
        if isinstance(parser_expecting_symbol, _grammar.NonTerminal):
            for production in grammar.productions_of(parser_expecting_symbol):
                item = Item(production, 0)
                if item not in item_set:
                    item_set.add(item)
                    queue.append(item)

    return item_set


def construct_transition(item_set, grammar):
    """Given an item set, construct all transitions from that item set.

    :param item_set: A set of Items, representing a parser state.
    :param grammar: The grammar the parser is parsing.
    :type grammar: Grammar
    :returns: The transitions, as a dict mapping a symbol (what was seen
        by the parser) to the item set that symbol transitions the parser to.
    """
    symbols = set()
    for item in item_set:
        expecting_symbol = item.expecting_symbol
        if expecting_symbol is not None:
            symbols.add(expecting_symbol)

    result = {}
    for symbol in symbols:
        new_item_set = set()
        for item in item_set:
            if item.expecting_symbol == symbol:
                new_item_set.add(item.advance())
        result[symbol] = closure(new_item_set, grammar)
    return result


def construct_all_transitions(grammar):
    """Construct all possible transitions for a given grammar.

    :param grammar: The grammar to construct transitions for.
    :type grammar: Grammar
    :returns: A dict mapping item sets to a transition table. The transition
        table is in the same format as construct_transition, that is, a mapping
        of a symbol being processed to the item set that symbol transitions the
        parser to.
    """
    first_item_set = frozenset((Item(grammar.starting_production, 0),))
    first_item_set = frozenset(closure(first_item_set, grammar))

    results = {}
    queue = collections.deque((first_item_set,))

    while queue:
        item_set = queue.popleft()
        if item_set in results:
            continue
        transitions = construct_transition(item_set, grammar)
        transitions = dict(
            (symbol, frozenset(item_set))
                for (symbol, item_set) in transitions.items())
        results[item_set] = transitions
        queue.extend(transitions.values())

    return results
