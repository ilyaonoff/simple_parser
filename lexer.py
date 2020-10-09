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

def make_lexer():
    return lex.lex()
