from __future__ import unicode_literals
from parglare.termui import s_header as _
from parglare.termui import s_attention as _a


class GrammarError(Exception):
    pass


class ParseError(Exception):
    def __init__(self, file_name, input_str, position, message_factory):
        from parglare.parser import pos_to_line_col
        self.file_name = file_name
        self.position = position
        self.line, self.column = pos_to_line_col(input_str, position)
        super(ParseError, self).__init__(
            message_factory(file_name, input_str, position))


# Error message factories
def _full_context(input_str, position):
    from parglare.parser import pos_to_line_col, position_context
    line, column = pos_to_line_col(input_str, position)
    context = position_context(input_str, position)
    return context, line, column


def nomatch_error(symbols):
    def _inner(file_name, input_str, position):
        context, line, column = _full_context(input_str, position)
        return (_a('Error') + ' {}at position ' + _a('{},{} ')
                + _('=>') + ' "{}". ' +
                _('Expected: ') + '{}').format(
                'in file "{}" '.format(file_name)
                if file_name else "",
                line, column, context,
                _(' or ').join(sorted([s.name for s in symbols])))
    return _inner


def disambiguation_error(tokens):
    def _inner(file_name, input_str, position):
        context, line, column = _full_context(input_str, position)
        return 'Error {}at position {},{} => "{}". ' \
            'Can\'t disambiguate between: {}'.format(
                'in file "{}" '.format(file_name)
                if file_name else "",
                line, column, context,
                _(' or ').join([str(t) for t in tokens]))
    return _inner


class ParserInitError(Exception):
    pass


class DisambiguationError(Exception):
    def __init__(self, tokens):
        self.tokens = tokens


class DynamicDisambiguationConflict(Exception):
    def __init__(self, state, token, actions):
        self.state = state
        self.token = token
        self.actions = actions

        from parglare.parser import SHIFT
        message = "{}\nIn state {}:{} and input symbol '{}' after calling"\
                  " dynamic disambiguation still can't decide "\
                  .format(str(state), state.state_id, state.symbol, token)
        if actions[0].action == SHIFT:
            prod_str = " or ".join(["'{}'".format(str(a.prod))
                                    for a in actions[1:]])
            message += "whether to shift or reduce by "\
                       "production(s) {}.".format(prod_str)
        else:
            prod_str = " or ".join(["'{}'".format(str(a.prod))
                                    for a in actions])
            message += "which reduction to perform: {}".format(prod_str)

        self.message = message

    def __str__(self):
        return self.message


class LRConflict(object):
    def __init__(self, state, term, productions):
        self.message = ""
        self.state = state
        self.term = term
        self.productions = productions

    @property
    def dynamic(self):
        return self.term in self.state.dynamic


class SRConflict(LRConflict):
    def __init__(self, state, term, productions):
        super(SRConflict, self).__init__(state, term, productions)
        prod_str = " or ".join(["'{}'".format(str(p))
                                for p in productions])
        message = "{}\nIn state {}:{} and input symbol '{}' can't " \
                  "decide whether to shift or reduce by production(s) {}." \
            .format(str(state), state.state_id, state.symbol, term, prod_str)
        if self.dynamic:
            message += " Dynamic disambiguation strategy will be called."
        self.message = message


class RRConflict(LRConflict):
    def __init__(self, state, term, productions):
        super(RRConflict, self).__init__(state, term, productions)
        prod_str = " or ".join(["'{}'".format(str(p))
                                for p in productions])
        message = "{}\nIn state {}:{} and input symbol '{}' can't " \
                  "decide which reduction to perform: {}." \
                  .format(str(state), state.state_id, state.symbol, term,
                          prod_str)
        if self.dynamic:
            message += " Dynamic disambiguation strategy will be called."
        self.message = message


class LRConflicts(Exception):
    def __init__(self, conflicts):
        self.conflicts = conflicts
        message = "\n{} conflicts in following states: {}"\
                  .format(self.kind,
                          set([c.state.state_id for c in conflicts]))
        super(LRConflicts, self).__init__(message)


class SRConflicts(LRConflicts):
    kind = "Shift/Reduce"


class RRConflicts(LRConflicts):
    kind = "Reduce/Reduce"
