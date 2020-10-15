from parsec import *
import sys
import argparse


class Node:
    def __init__(self, name, needToWrite, childs=[]):
        self.name = name
        self.childs = childs
        self.needToWrite = needToWrite

    def printIndent(self, indent):
        result = '|'
        for _ in range(0, indent):
            result += '  |'
        return result

    def stringRepresentation(self, indent=0):
        result = ""
        if self.needToWrite:
            result = self.printIndent(indent) + self.name + '\n'
        for child in self.childs:
            result += child.stringRepresentation(
                indent + int(self.needToWrite)) + '\n'
        return result[:-1]

    def __str__(self):
        return self.stringRepresentation()


spaces = regex(r'\s*', re.MULTILINE)
ident = regex(r'(?!(module\b|type\b))[a-z_][a-zA-Z0-9_]*')
var = regex(r'[A-Z][a-zA-Z0-9_]*')


@generate
def Id():
    curIdent = yield spaces >> ident << spaces
    return Node(f'Id : \'{curIdent}\'', True)


@generate
def Var():
    curVar = yield spaces >> var << spaces
    return Node(f'Var : \'{curVar}\'', True)

def eps():
    return Node('EPSILON', True)


@generate
def Prolog():
    module = yield spaces >> (Module | string('')) << spaces
    if module == '':
        module = Node('Module', True, [eps()])
    types = yield spaces >> TypeSeq << spaces
    relations = yield spaces >> RelationSeq << spaces
    return Node('Prolog', True, [module, types, relations])


@generate
def Module():
    yield spaces >> regex(r'module\b') << spaces
    moduleIdent = yield Id << spaces << string('.')
    return Node("Module", True, [moduleIdent])


@generate
def Atom():
    headerId = yield spaces >> Id << spaces
    atomSeq = yield AtomSuf
    return Node('Atom', True, [headerId, atomSeq])


@generate
def AtomSuf():
    arg = yield spaces >> (Id | Var | List | (string('(') >> SthInBrackets << string(')')) | string('')) << spaces
    if arg == '':
        return Node('AtomSuf', True, [eps()])
    cont = yield spaces >> AtomSuf << spaces
    return Node('AtomSuf', True, [arg, cont])


def nil():
    return Node('Atom', True, [Node('Id : \'nil\'', True), Node('AtomSuf', True, [eps()])])


def cons(el, suf):
    return Node('Atom', True, [Node('Id : \'cons\'', True), Node('AtomSuf', True, [el, Node('AtomSuf', True, [suf])])])


@generate
def List():
    el = yield spaces >> string('[') >> spaces >> (Elem | string(']')) << spaces
    if el == ']':
        return nil()
    delimitr = yield spaces >> (string('|') | string(',') | string(']'))
    if delimitr == '|':
        suf = yield spaces >> Var << spaces << string(']')
        return cons(el, suf)
    elif delimitr == ',':
        suf = yield spaces >> ElemSeq << spaces << string(']')
        return cons(el, suf)
    return cons(el, nil())


@generate
def ElemSeq():
    el = yield spaces >> Elem << spaces
    rest = yield spaces >> (string(',') | string('')) << spaces
    if rest == '':
        return cons(el, nil())
    seq = yield spaces >> ElemSeq << spaces
    return cons(el, seq)


@generate
def Elem():
    el = yield spaces >> (Atom | Var | List) << spaces
    return Node('Elem', False, [el])


@generate
def SthInBrackets():
    el = yield spaces >> (string('(') >> SthInBrackets << (string(')')) | Elem) << spaces
    return Node('SthInBrackets', False, [el])


@generate
def RelationSeq():
    rel = yield spaces >> (Relation | string('')) << spaces
    if rel == '':
        return Node('RelationSeq', True, [eps()])
    rest = yield RelationSeq
    return Node('RelationSeq', True, [rel, rest])


@generate
def Relation():
    atom = yield spaces >> Atom << spaces
    afterAtom = yield (string(':-') | string('.')) << spaces
    if afterAtom == '.':
        return Node('Relation', True, [atom])
    body = yield spaces >> Expression << spaces << string('.') << spaces
    return Node('Relation', True, [atom, body])


@generate
def Expression():
    term = yield spaces >> Term << spaces
    afterTerm = yield spaces >> (string(';') | string('')) << spaces
    if afterTerm == '':
        return Node('Expression', False, [term])
    rest = yield spaces >> Expression << spaces
    return Node('Disj', True, [term, rest])


@generate
def Term():
    left = yield spaces >> ((string('(') >> spaces >> Expression << spaces << string(')')) | Atom) << spaces
    afterLeft = yield spaces >> (string(',') | string('')) << spaces
    if afterLeft == '':
        return Node('Term', False, [left])
    right = yield spaces >> Term << spaces
    return Node('Conj', True, [left, right])


@generate
def TypeSeq():
    typeDef = yield spaces >> (TypeDef | string('')) << spaces
    if typeDef == '':
        return Node('TypeDef', True, [eps()])
    rest = yield TypeSeq
    return Node('TypeSeq', True, [typeDef, rest])


@generate
def TypeDef():
    typeId = yield spaces >> regex(r'type\b') >> spaces >> Id << spaces
    type = yield spaces >> Type << spaces << string('.') << spaces
    return Node('TypeDef', True, [typeId, type])


@generate
def Type():
    first = yield spaces >> ((string('(') >> Type << string(')')) | Atom | Var) << spaces
    maybeArrow = yield spaces >> (string('->') | string('')) << spaces
    if maybeArrow == '':
        return Node('Type', False, [first])
    rest = yield spaces >> Type << spaces
    return Node('Arrow', True, [first, rest])


def parseProlog(inputText, parserType=Prolog, output=None):
    parser = parserType + eof()
    try:
        result = parser.parse(inputText)
    except ParseError as e:
        if output:
            lineNo, posInLine = e.loc_info(e.text, e.index)

            errorInfo = f'Line {lineNo}, column {posInLine}. '
            errorInfo += 'Syntax error:\n\n' + \
                inputText.split('\n')[lineNo] + '\n'
            errorInfo += posInLine * \
                '-' + '^' + '\n'

            output.write(errorInfo)
        return False
    else:
        if output:
            output.write(str(result[0]))
        return True


def parseFile(fileName, parserType):
    with open(fileName) as file:
        input = file.read()

    with open(f'{fileName}.out', 'w') as file:
        return parseProlog(input, parserType, file)


if __name__ == "__main__":
    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument("--atom", type=str)
    argumentParser.add_argument("--typeexpr", type=str)
    argumentParser.add_argument("--type", type=str)
    argumentParser.add_argument("--module", type=str)
    argumentParser.add_argument("--relation", type=str)
    argumentParser.add_argument("--list", type=str)
    argumentParser.add_argument("--prog", type=str)

    args = argumentParser.parse_args()

    if args.atom:
        parseFile(args.atom, Atom)
    elif args.typeexpr:
        parseFile(args.typeexpr, Type)
    elif args.type:
        parseFile(args.type, TypeDef)
    elif args.module:
        parseFile(args.module, Module)
    elif args.relation:
        parseFile(args.relation, Relation)
    elif args.list:
        parseFile(args.list, List)
    elif args.prog:
        parseFile(args.prog, Prolog)
    elif len(sys.argv) == 2:
        parseFile(sys.argv[1], Prolog)
