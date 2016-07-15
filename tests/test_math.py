import unittest
import numpy as np

from simpletex import write, clear, dump
from simpletex.math import Divide, Matrix

DATA = [[1, 2], [3, 4]]
NP_DATA = np.array(DATA)
MAT_ENV = '\\begin{{Bmatrix}}\n{}\n\\end{{Bmatrix}}'


class TestDivide(unittest.TestCase):
    def setUp(self):
        clear()

    def test_call_display(self):
        div = Divide()
        self.assertEqual(str(div(3, 5)), r'\frac{3}{5}')

    def test_call_inline(self):
        div = Divide(inline=True)
        self.assertEqual(str(div(3, 5)), r'3/5')

    def test_write_display(self):
        with Divide():
            write(3)
            write(5)
        self.assertEqual(dump(), r'\frac{3}{5}')

    def test_write_inline(self):
        with Divide(inline=True):
            write(3)
            write(5)
        self.assertEqual(dump(), r'3/5')

    def test_error_invalid(self):
        self.assertRaises(ValueError, Divide(), 3)

    def test_error_short(self):
        self.assertRaises(ValueError, Divide(), [3])

    def test_error_long(self):
        self.assertRaises(ValueError, Divide(), [3, 1, 4])

class TestMatrix(unittest.TestCase):
    def setUp(self):
        self.mat = Matrix(brackets='{')
        clear()

    def test_empty(self):
        self.assertEqual(str(self.mat('')), MAT_ENV.format(''))

    def test_call_no_numpy(self):
        self.assertEqual(self.mat(DATA),
                         MAT_ENV.format('\t1 & 2 \\\\\n\t3 & 4 \\\\'))

    def test_call_numpy(self):
        self.assertEqual(self.mat(NP_DATA),
                         MAT_ENV.format('\t1 & 2 \\\\\n\t3 & 4 \\\\'))

    def test_write(self):
        with self.mat:
            for line in DATA:
                write(line)
        self.assertEqual(dump(),
                         MAT_ENV.format('\t1 & 2 \\\\\n\t3 & 4 \\\\'))
