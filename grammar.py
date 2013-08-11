"""Classes to represent the grammar of a language."""


class Terminal(object):
    """Represents a terminal in the grammar.

    A terminal is something that appears in a string generated by the grammar.
    For example, in Python, the string "raise" might be a terminal. These are
    the deepest nodes the the AST, and what you actually see in grammar being
    parsed.

    Typically, a lexer would output these, to feed them into a parser.
    """

    def __init__(self, text, is_literal=True):
        self.name = text
        self.is_literal = is_literal

    def __str__(self):
        if self.is_literal:
            return '"{}"'.format(self.name.replace('"', '""'))
        else:
            return '?{}?'.format(self.name.replace('?', '??'))

    def __repr__(self):
        return '<Terminal {}>'.format(self)


class NonTerminal(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        visual_name = self.name
        visual_name = visual_name.replace('\\', '\\\\')
        visual_name = self.name.replace('<', '\\<').replace('>', '\\>')
        return '<{0}>'.format(visual_name)

    def __repr__(self):
        return '<NonTerminal {}>'.format(self)


class Production(object):
    def __init__(self, non_terminal, production):
        self.non_terminal = non_terminal
        self.produces = tuple(production)

    def __str__(self):
        return '{0} ::= {1}'.format(
            self.non_terminal,
            ' '.join(str(i) for i in self.produces))

    def __repr__(self):
        return '{}.{}({!r}, {!r})'.format(
                self.__module__, type(self).__name__,
                self.non_terminal, self.produces)

    def __eq__(self, other):
        return (self.non_terminal == other.non_terminal
                and self.produces == other.produces)

    def __hash__(self):
        return hash((self.non_terminal, self.produces))
