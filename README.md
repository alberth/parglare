# parglare

A pure Python Scannerless LR parser (will be GLR soon) with LALR or SLR tables.

- Free software: MIT license
- Documentation: TODO

This lib is in the early phase of development. It is not tested extensively yet.
Do not use it for anything important.


# What is done so far

- Textual syntax for grammar specification. Parsed with parglare.
- SLR and LALR tables calculation (LALR is the default)
- Scannerless LR(1) parsing
  - Scanner is integrated into parsing. This give more power as the token
    recognition is postponed and done in the parsing context at the current
    parsing location.
- Declarative associativity and priority based conflict resolution for productions
  - See the `calc` example, or the quick intro bellow.
- Lexical disambiguation strategy.
  - The default strategy is longest-match first and than str over regex match
    (i.e. the most specific match). Terminal priority can be provided for
    override if necessary.
- Semantic actions and default actions which builds the parse tree (controlled
  by `actions` and `default_actions` parameters for the `Parser` class).
  - If no actions are provided and default actions are explicitely disabled
    parser works as recognizer, i.e. no reduction actions are called and the
    only output of the parser is whether the input was recognized or not.
- Debug print/tracing (set `debug=True` to the `Parser` instantiation).
- Tests
- Few examples (see `examples` folder)

# TODO

- Docs
- Tables caching/loading (currently tables are calculated whenever `Parser` is
  instantiated)
- Support for language comments. Whitespace handling which is currently provided
  will be integrated with comment support.
- GLR parsing (Tomita's algorithm)
- Error recovery

# Quick intro

This is just a small example to get the general idea. Until docs is done see
the `example` folder and `tests` for more.

```python
from parglare import Parser, Grammar

grammar = r"""
E = E '+' E  {left, 1}
  | E '-' E  {left, 1}
  | E '*' E  {left, 2}
  | E '/' E  {left, 2}
  | E '^' E  {right, 3}
  | '(' E ')';
E = number;
number = /\d+(\.\d+)?/;
"""

actions = {
    "E:0": lambda _, nodes: nodes[0] + nodes[2],
    "E:1": lambda _, nodes: nodes[0] - nodes[2],
    "E:2": lambda _, nodes: nodes[0] * nodes[2],
    "E:3": lambda _, nodes: nodes[0] / nodes[2],
    "E:4": lambda _, nodes: nodes[0] ** nodes[2],
    "E:5": lambda _, nodes: nodes[1],
    "E:6": lambda _, nodes: nodes[0],
    "number": lambda _, value: float(value),
}

g = Grammar.from_string(grammar)
parser = Parser(g, debug=True, actions=actions)

result = parser.parse("34 + 4.6 / 2 * 4^2^2 + 78")

print("Result = ", result)

# Output
# -- Debuging/tracing output with detailed info about grammar, productions,
# -- terminals and nonterminals, DFA states, parsing progress,
# -- and at the end of the output:
# Result = 700.8
```

Credits
---------

Initial layout/content of this package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
