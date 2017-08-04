import unittest

from pyeval.indentation import dedent, indent



class indentationTests (unittest.TestCase):

    def test_dedentAndIndent(self):
        x = """
          cheer:
            whoop!
          effect:
             wham!

        """

        expectedDedent = 'cheer:\n  whoop!\neffect:\n   wham!\n'

        dedented = dedent(x)

        self.assertEqual(expectedDedent, dedented)
        self.assertEqual(dedented, indent(dedented, 0))

        expectedIndent = x[1:].rstrip() + '\n'

        self.assertEqual(expectedIndent, indent(dedented, 10))
