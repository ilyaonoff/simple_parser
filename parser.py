from parsec import *
import sys
import argparse
'''
------------Grammar---------------
Prolog   -> Module? TypeSeq? RelationSeq?
Module   -> 'module' Id.



TypeSeq  -> TypeDecl TypeSeq | TypeDecl
TypeDecl -> 'type' Id Type.
Type     -> Atom | (Type) | Atom -> Type | (Type) -> Type | Var | Var -> Type




Var      -> [A-Z][a-zA-Z0-9_]*
Id       -> [a-z_][a-zA-Z0-9_]*
List     -> [] | [Elem, ElemSeq] | [B]
B        -> Atom '|' Var | Var '|' Var | List '|' Var 
ElemSeq  -> Elem , ElemSeq | Elem 
Elem     -> Var | Atom | List
Atom     -> Id AtomSeq | Id
AtomSeq  -> Id AtomSeq? | (SthInBrackets) AtomSeq? | Var AtomSeq? | List AtomSeq?
SthInBrackets -> (SthInBrackets) | Elem

RelationSeq -> Relation RelationSeq | Relation
Relation    -> Atom :- Expression.  | Atom.
Expression  -> Term ; Expression | Term
Term        -> (Expression) , Term | (Expression)
                | Atom , Term | Atom
'''


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


@generate
def Prolog():
    module = yield spaces >> (Module | string('')) << spaces
    if module == '':
        module = Node('Module', True, [Node('EPSILON', True)])
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
    atomSeq = yield AtomSeq
    return Node('Atom', True, [headerId, atomSeq])


@generate
def AtomSeq():
    arg = yield spaces >> (Id | Var | List | (string('(') >> SthInBrackets << string(')')) | string('')) << spaces
    if arg == '':
        return Node('AtomSeq', True)
    cont = yield spaces >> AtomSeq << spaces
    return Node('AtomSeq', True, [arg, cont])


def nil():
    return Node('Atom', True, [Node('Id : \'nil\'', True), Node('AtomSeq', True)])


@generate
def List():
    el = yield spaces >> string('[') >> spaces >> (Elem | string(']')) << spaces
    if el == ']':
        return nil()
    delimitr = yield spaces >> (string('|') | string(',') | string(']'))
    if delimitr == '|':
        suf = yield spaces >> Var << spaces << string(']')
        return Node('Atom', True, [Node('Id : \'cons\'', True), el, Node('AtomSeq', True, [suf])])
    elif delimitr == ',':
        suf = yield spaces >> ElemSeq << spaces << string(']')
        return Node('Atom', True, [Node('Id : \'cons\'', True), el, Node('AtomSeq', True, [suf])])
    return Node('Atom', True, [Node('Id : \'cons\'', True), el, Node('AtomSeq', True, [nil()])])


@generate
def ElemSeq():
    el = yield spaces >> Elem << spaces
    rest = yield spaces >> (string(',') | string('')) << spaces
    if rest == '':
        return Node('Atom', True, [Node('Id : \'cons\'', True), el, Node('AtomSeq', True, [nil()])])
    seq = yield spaces >> ElemSeq << spaces
    return Node('Atom', True, [Node('Id : \'cons\'', True), el, Node('AtomSeq', True, [seq])])


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
        return Node('RelationSeq', True, [Node('EPSILON', False)])
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
        return Node('Expression', term.needToWrite, [term])
    rest = yield spaces >> Expression << spaces
    return Node('Expression', True, [term, rest])  # TODO


@generate
def Term():
    left = yield spaces >> ((string('(') >> spaces >> Expression << spaces << string(')')) | Atom) << spaces
    afterLeft = yield spaces >> (string(',') | string('')) << spaces

    needWrite = True
    if left.name == 'Expression':
        needWrite = False

    if afterLeft == '':
        return Node('Term', needWrite, [left])
    right = yield spaces >> Term << spaces
    return Node('Term', True, [left, right])


@generate
def TypeSeq():
    typeDef = yield spaces >> (TypeDef | string('')) << spaces
    if typeDef == '':
        return Node('TypeDef', True, [Node('EPSILON', True)])
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

    needWrite = True
    if first.name == 'Type':
        needWrite = False

    if maybeArrow == '':
        return Node('Type', needWrite, [first])
    rest = yield spaces >> Type << spaces
    return Node('Type', True, [first, rest])


def parseProlog(inputText, P=Prolog, output=None):
    parser = P + eof()
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


def parseFile(fileName, P):
    with open(fileName) as file:
        input = file.read()

    with open(f'{fileName}.out', 'w') as file:
        return parseProlog(P, input, file)


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
