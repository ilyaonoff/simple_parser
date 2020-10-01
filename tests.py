import unittest
import parser as prs

class TestParser(unittest.TestCase):
    def test_many_brackets(self):
        case1 = prs.Parser('f :- (a;b),(((c,d;(a)))),((a,b),((c);d);(a,d,c));(a).')
        case2 = prs.Parser('Id_1_2_f :- (_1;_2,(a2);(aaa),(a);(b_b)).')
        self.assertTrue(case1.program())
        self.assertTrue(case2.program())
 
    def test_many_whitespaces_and_tabs(self):
        parser = prs.Parser('             f            :-\t\t\t\t g\t    \t ,h\t\t\t\t    .')
        self.assertTrue(parser.program())

    def test_many_newlines(self):
        parser = prs.Parser('\n\n\n\nf\n\n\n    :-\n  (\nf;\n\n\t\t\n h)\n.')
        self.assertTrue(parser.program())

    def test_several_relations(self):
        case1 = prs.Parser('f.\nf :- g.\n f :- g, h; t.\nf :- g, (h; t).')
        case2 = prs.Parser('_id1:-_id1;_id2.\n\nf :- \n\n g\n,h\t\t.head :- body.only_head.')
        self.assertTrue(case1.program())
        self.assertTrue(case2.program())

    def test_incorrect_bracket_sequance(self):
        case1 = prs.Parser('f:-(fasdfjas;fdkasd,(aaa;(b));(c).')
        case2 = prs.Parser('f:-f,h;(k;(l,m.')
        self.assertFalse(case1.program())
        self.assertFalse(case2.program())

    def test_incorrect_relation_declaration(self):
        self.assertFalse(prs.Parser('f').program())
        self.assertFalse(prs.Parser(':- f.').program())
        self.assertFalse(prs.Parser('f :- .').program())
        self.assertFalse(prs.Parser('f :- g;h, .').program())
        self.assertFalse(prs.Parser('f:-(g, h) :- k, l, m.').program())
        self.assertFalse(prs.Parser('a :- aa(aa).\n\nb_b \n:-\ng;;h.').program())


if __name__ == '__main__':
    unittest.main()
