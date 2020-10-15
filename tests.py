from parser import parseProlog as parse
import unittest


class Test(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
