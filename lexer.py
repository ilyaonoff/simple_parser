import ply.lex as lex
import sys

tokens = [
    'DOT',
    'AND',
    'OR',
    'OPEN_BRACKET',
    'CLOSE_BRACKET',
    'CORKSCREW',
    'ID'
]

t_DOT = r'\.'
t_AND = r'\,'
t_OR = r'\;'
t_OPEN_BRACKET = r'\('
t_CLOSE_BRACKET = r'\)'
t_CORKSCREW = r':-'
t_ID = r'[a-zA-Z_][a-zA-Z_0-9]*'

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

class Lexer:
    def __init__(self, input):
        self.lexer = lex.lex()
        self.input = input
        self.lexer.input(input)

    def token(self):
        buffer = self.lexer.token()
        return buffer

    def compute_column(self, token):
        line_start = self.input.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1
