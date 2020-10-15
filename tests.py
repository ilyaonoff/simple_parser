from parser import parseProlog as parse
import unittest


class compatibilityTests(unittest.TestCase):
    def test_correct(self):
        self.assertTrue(parse(
            'f.\nf :- g.\n f :- g, h; t.\n f :- g, (h; t).\nf a :- g, h (t c d).\nf (cons h t) :- g h, f t.'))
        self.assertTrue(parse(
            'odd (cons H (cons H1 T)) (cons H T1) :- odd T T1. \n odd (cons H nil) nil. \nodd nil nil.'))
        self.assertTrue(
            parse('f :- (((g))).\nf :- a ((((b)))).\nf  :- a (a (a)).'))
        self.assertTrue(parse('f :- (a b) , (c d). '))
        self.assertTrue(parse(
            'a \n\n\tb (((\naa\n)\n)\n)\n\n\n\n.f ((((a ((((b)))))))) :- (((((a (b)))))).'))
        self.assertTrue(parse('a b c d e f g h. q w e r t :- q w e r t.'))
        self.assertTrue(
            parse('one two (three (four)) :- ((a));(b,c;d a a a ;(a)).'))
        self.assertTrue(parse('a (b c (d)) :- a;(a b,c,d).'))
        self.assertTrue(parse('f (a (b c) d (e (f g))).'))

    def test_incorrect(self):
        self.assertFalse(parse('(a b) c.'))
        self.assertFalse(parse('a ((b) c).'))
        self.assertFalse(parse('f :- a ((a b) (a b)).'))
        self.assertFalse(parse('a (a b )))))).'))
        self.assertFalse(parse('head'))
        self.assertFalse(parse('head :- body'))
        self.assertFalse(parse('f :- g; h, .'))
        self.assertFalse(parse('f :- (g; (f).'))
        self.assertFalse(parse('f ().'))
        self.assertFalse(parse('(((b))).'))
        self.assertFalse(parse('.'))
        self.assertFalse(parse('head :- id ;;;;; id.'))
        self.assertFalse(parse('a (a ; b, c).'))
        self.assertFalse(parse('f (c;c;c) :- b.'))
        self.assertFalse(parse('h :- a (a ; b).'))
        self.assertFalse(parse('f ( :- ) h.'))
        self.assertFalse(parse('f :- g.....'))
        self.assertFalse(parse('f\ng.\nf :- a ((f;g).\nf ).'))
        self.assertFalse(parse('f :- g \ng :- f.'))
        self.assertFalse(parse('f.f :- .\nf g :- f ((b);), h.'))
        self.assertFalse(parse('\\\\\\.'))
        self.assertFalse(parse('f \ (g h) :- h.'))
        self.assertFalse(parse('f :.'))


class unitTests(unittest.TestCase):
    def test_atom(self):
        from parser import Atom

        self.assertTrue(parse("a", Atom))
        self.assertTrue(parse("a b c", Atom))
        self.assertTrue(parse("a (b c)", Atom))
        self.assertTrue(parse("a ((b c))", Atom))
        self.assertTrue(parse("a ((b c)) d", Atom))
        self.assertTrue(parse("a ((b c))  (d)", Atom))
        self.assertTrue(parse("a ((b  c))  (d)", Atom))
        self.assertTrue(parse("a ((b  c) )  ( d )", Atom))
        self.assertTrue(parse("a((b c))(d)", Atom))

        self.assertFalse(parse("a (a", Atom))
        self.assertFalse(parse("X a", Atom))
        self.assertFalse(parse("(a)", Atom))

    def test_relation(self):
        from parser import Relation

        self.assertTrue(parse("a.", Relation))
        self.assertTrue(parse("a b.", Relation))
        self.assertTrue(parse("a:-a.", Relation))
        self.assertTrue(parse("a :-a.", Relation))
        self.assertTrue(parse("a:-a b.", Relation))
        self.assertTrue(parse("a b:- (a b)  .", Relation))
        self.assertTrue(parse("a b:- a;b,c.", Relation))
        self.assertTrue(parse("a b:- a;(b,c).", Relation))
        self.assertTrue(parse("a b:- (a;b),c.", Relation))
        self.assertTrue(parse("a b:- a;b;c.", Relation))
        self.assertTrue(parse("a b:- a,b,c.", Relation))
        self.assertTrue(parse("a (b (c))  :- (a b) .", Relation))

    def test_typeExpr(self):
        from parser import Type

        self.assertTrue(parse("a", Type))
        self.assertTrue(parse("Y -> X", Type))
        self.assertTrue(parse("(Y -> X)", Type))
        self.assertTrue(parse("(A -> B) -> C", Type))
        self.assertTrue(parse("A -> B -> C", Type))
        self.assertTrue(parse("list (list A) -> list A -> o", Type))
        self.assertTrue(
            parse("pair A B -> (A -> C) -> (B -> D) -> pair C D", Type))

    def test_type(self):
        from parser import TypeDef

        self.assertTrue(parse("type a b.", TypeDef))
        self.assertTrue(parse("type a b -> X.", TypeDef))
        self.assertTrue(
            parse("type filter (A -> o) -> list a -> list a -> o.", TypeDef))
        self.assertTrue(
            parse("type filter (A -> o) -> list A -> list A -> o.", TypeDef))
        self.assertTrue(parse("type a (((b))).", TypeDef))
        self.assertTrue(parse("type d a -> (((b))).", TypeDef))

        self.assertFalse(parse("type type type -> type.", TypeDef))
        self.assertFalse(parse("type x -> y -> z.", TypeDef))
        self.assertFalse(parse("tupe x o.", TypeDef))

    def test_module(self):
        from parser import Module

        self.assertTrue(parse("module name.", Module))
        self.assertTrue(parse(" \t\nmodule\n\n  name_123.", Module))

        self.assertFalse(parse("modulo name.", Module))
        self.assertFalse(parse("module module.", Module))
        self.assertFalse(parse("modulename.", Module))
        self.assertFalse(parse("mod ule name.", Module))
        self.assertFalse(parse("module 123name.", Module))
        self.assertFalse(parse("module name!", Module))

    def test_list(self):
        from parser import List

        self.assertTrue(parse("[]", List))
        self.assertTrue(parse("[a]", List))
        self.assertTrue(parse("[A,B]", List))
        self.assertTrue(parse("[a (b c), B, C]", List))
        self.assertTrue(parse("[a | T]", List))
        self.assertTrue(parse("[ [a] | T ]", List))
        self.assertTrue(parse("[ [H | T], a ]", List))

        self.assertFalse(parse("[a | a]", List))
        self.assertFalse(parse("[A,B,]", List))
        self.assertFalse(parse("[A,B", List))
        self.assertFalse(parse("][", List))


class integrateTests(unittest.TestCase):
    def test_correct(self):
        self.assertTrue(parse("module id."))
        self.assertTrue(parse('type a o -> a [a|B].'))
        self.assertTrue(parse('a a a (((a))) :- a a ([A|A]).'))
        self.assertTrue(parse('''
                                    module name.

                                    type fruit (A -> o) -> (((b))).
                                    type veg a.

                                    fruit [x, y, z] :- g [x y [z|B]|B].
                                    head.
                                    head :- one;two,three.
                              '''))
        self.assertTrue(parse('''
                                    type name (A -> x [x, y, z]) -> a [[X|Y]|Z].

                                    head a [h1, h2, h3] (((a))) b :- a [x, y];b,a a [a]; a (((a))).
                                    f [].
                              '''))
        self.assertTrue(parse('''
                                    module name.

                                    type t t t t -> (((t))) -> list [] -> list [[]|T].
                                    type a b [X, Y, [[[Z]]]] -> (A -> B -> C) -> (D -> E -> G -> f [x, y]).

                                    a.b.c.
                                    head a A AA AAA [A_1, A_2, A_3] :- (a;b;c;d),l [].

                              '''))

    def test_incorrect(self):
        self.assertFalse(parse("module."))
        self.assertFalse(parse('type -> a [a|B].'))
        self.assertFalse(parse('a a a (((a))) :- A a ([A|A]).'))
        self.assertFalse(parse('''
                                    module modules.
                                    type a a.
                                    type name [X|Y].
                               '''))
        self.assertFalse(parse(''' 
                                    type f f -> f.
                                    [f, x, y] z.
                               '''))
        self.assertFalse(parse('''
                                    module id.
                                    type id
                                    f f :- f;f
                               '''))


if __name__ == "__main__":
    unittest.main()
