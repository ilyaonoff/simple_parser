from lexer import tokens, make_lexer, IllegalCharException
import ply.yacc as yacc
import sys

'''
----------Grammar----------

Program        -> Relation Program   | EPSILON
Relation       -> Atom :- Expression.  | Atom.
Expression     -> Term ; Expression | Term
Term           -> (Expression) , Term | (Expression)
                | Atom , Term | Atom
Atom           -> Id AtomsSeq
AtomsSeq       -> Id AtomsSeq | (AtomInBrackets) AtomsSeq | EPSILON
AtomInBrackets -> (AtomInBrackets) | Atom
Id             -> [a-zA-Z_][a-zA-Z_0-9]*
'''


class Node:
    def __init__(self, name, childs=[]):
        self.name = name
        self.childs = childs

    def printIndent(self, indent):
        result = '|'
        for _ in range(0, indent):
            result += '  |'
        return result

    def stringRepresentation(self, indent=0):
        result = self.printIndent(indent) + self.name + '\n'
        for child in self.childs:
            result += child.stringRepresentation(indent + 1) + '\n'
        return result[:-1]


def p_program(p):
    '''
    program : relation program
            | empty
    '''
    if len(p) == 3:
        p[0] = Node('Program', [p[1], p[2]])
    else:
        p[0] = Node('Program', [p[1]])


def p_relation(p):
    '''
    relation : atom DOT
             | atom CORKSCREW expression DOT
    '''
    if len(p) == 3:
        p[0] = Node('Relation', [p[1], Node('DOT : \'.\'')])
    else:
        p[0] = Node('Relation', [p[1],
                                 Node('CORKSCREW : \':-\''), p[3], Node('DOT : \'.\'')])


def p_expression(p):
    '''
    expression : term OR expression
               | term
    '''
    if len(p) == 2:
        p[0] = Node('Expression', [p[1]])
    else:
        p[0] = Node('Expression', [p[1], Node('OR : \';\''), p[3]])


def p_term_without_brackets(p):
    '''
    term : atom AND term
         | atom
    '''
    if len(p) == 4:
        p[0] = Node('Term', [p[1], Node('AND : \',\''), p[3]])
    else:
        p[0] = Node('Term', [p[1]])


def p_term_with_brackets(p):
    '''
    term : OPEN_BRACKET expression CLOSE_BRACKET AND term
         | OPEN_BRACKET expression CLOSE_BRACKET
    '''
    if len(p) == 6:
        p[0] = Node('Term', [Node('LBR : \'(\''), p[2],
                             Node('RBR : \')\''), Node('AND : \',\''), p[5]])
    else:
        p[0] = Node('Term', [Node('LBR : \'(\''), p[2], Node('RBR : \')\'')])


def p_atom(p):
    '''
    atom : id atomsSeq
    '''
    p[0] = Node('Atom', [p[1], p[2]])


def p_atomsSeq(p):
    '''
    atomsSeq : id atomsSeq
             | OPEN_BRACKET atomInBrackets CLOSE_BRACKET atomsSeq
             | empty
    '''
    if len(p) == 3:
        p[0] = Node('AtomsSeq', [p[1], p[2]])
    elif len(p) == 5:
        p[0] = Node(
            'AtomsSeq', [Node('LBR : \'(\''), p[2], Node('RBR : \')\''), p[4]])
    else:
        p[0] = Node('AtomsSeq', [p[1]])


def p_atom_in_brackets(p):
    '''
    atomInBrackets : OPEN_BRACKET atomInBrackets CLOSE_BRACKET
                   | atom
    '''
    if len(p) == 4:
        p[0] = Node('AtomInBrackets',
                    [Node('LBR : \'(\''), p[2], Node('RBR : \')\'')])
    else:
        p[0] = Node('AtomInBrackets', [p[1]])


def p_empty(p):
    'empty :'
    p[0] = Node('EPSILON')


def p_id(p):
    'id : ID'
    p[0] = Node(f'ID : \'{p[1]}\'')


def find_column(input, lexpos):
    line_start = input.rfind('\n', 0, lexpos) + 1
    return (lexpos - line_start) + 1


inputText = ""
wasError = False
errorsInfo = ""


def p_error(p):
    global wasError, errorsInfo
    wasError = True
    if not p:
        errorsInfo += 'Unexpected end of file.\n'
    else:
        errorsInfo += f'Line {p.lineno}, column {find_column(inputText, p.lexpos)}. '
        errorsInfo += 'Syntax error:\n\n' + \
            inputText.split('\n')[p.lineno - 1] + '\n'
        errorsInfo += (find_column(inputText, p.lexpos) - 1) * \
            '-' + '^' + '\n\n'


def make_parser():
    lexer = make_lexer()
    parser = yacc.yacc()
    return parser


def parse(inputProgram, output=None):
    parser = make_parser()

    global inputText, errorsInfo, wasError
    inputText = inputProgram

    try:
        result = parser.parse(inputText, tracking=True)
    except IllegalCharException as e:
        wasError = True
        errorsInfo += e.info()

    if output:
        if wasError:
            output.write(errorsInfo)
        else:
            output.write(result.stringRepresentation())

    return not wasError


if __name__ == "__main__":
    with open(sys.argv[1]) as file:
        input = file.read()

    with open(f'{sys.argv[1]}.out', 'w') as file:
        parse(input, file)
