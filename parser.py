import lexer as lex
import sys


class Parser:
    class Verdict:
        def __init__(self, initMessage, isError=False):
            self.message = initMessage
            self.isError = isError

        def __bool__(self):
            return not self.isError

        def __str__(self):
            return self.message

    def __init__(self, input):
        self.lexer = lex.Lexer(input)
        self.curToken = self.lexer.token()

    def createErrorVerdict(self, expectedToken):
        if not self.curToken:
            return self.Verdict('Attention, there is a syntax error!!!\n\n'
                                'INFO:\n'
                                'Unexpected end of file. ', True)

        return self.Verdict('Attention, there is a syntax error!!! \n\nINFO:\n'
                            f'Line: {self.curToken.lineno}, Coloumn: {self.lexer.compute_column(self.curToken)}\n'
                            f'Expected \'{expectedToken}\', but received \'{self.curToken.value}\'', True)

    def accept(self, tokenType):
        if self.curToken and self.curToken.type == tokenType:
            self.curToken = self.lexer.token()
            return True
        return False

    def program(self):
        """
        Program -> Relation Program | epsilon
        """
        if not self.curToken:
            return self.Verdict('OK')

        left = self.relation()
        if not left:
            return left

        right = self.program()
        if not right:
            return right

        return self.Verdict('OK')

    def relation(self):
        """
        Relation -> ID. | ID :- Expression.
        """
        left = self.id()
        if not left:
            return left

        if self.accept('DOT'):
            return self.Verdict('OK')

        if self.accept('CORKSCREW'):
            right = self.expression()
            if not right:
                return right

            if self.accept('DOT'):
                return self.Verdict('OK')

        return self.createErrorVerdict('.')

    def expression(self):
        """
        Expression -> StrongExpr;Expression | StrongExpr
        """
        left = self.strongExpr()
        if not left:
            return left

        if self.accept('OR'):
            right = self.expression()
            if not right:
                return right

        return self.Verdict('OK')

    def strongExpr(self):
        """
        StrongExpr -> ID,StrongExpr | (Expression),StrongExpr | (Expression) | ID 
        """
        if self.accept('OPEN_BRACKET'):
            left = self.expression()
            if not left:
                return left

            if not self.accept('CLOSE_BRACKET'):
                return self.createErrorVerdict(')')

            if self.accept('AND'):
                right = self.strongExpr()
                if not right:
                    return right

            return self.Verdict('OK')

        left = self.id()
        if not left:
            return left

        if self.accept('AND'):
            right = self.strongExpr()
            if not right:
                return right

        return self.Verdict('OK')

    def id(self):
        """
        ID -> [a-zA-Z_][a-zA-Z_0-9]*
        """
        if self.accept('ID'):
            return self.Verdict('OK')

        return self.createErrorVerdict('identifier')


if __name__ == "__main__":
    with open(sys.argv[1]) as file:
        input = file.read()
    parser = Parser(input)
    print(parser.program())
