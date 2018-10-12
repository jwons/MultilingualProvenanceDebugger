import unittest
import pandas as pd
from Parse import Parser

class TestProvParser(unittest.TestCase):

    def setUp(self):
        self.prov = Parser("tests/test.json")
    
    def testConstruction(self):
        self.assertIsNot(self.prov._provElements, {})
        self.assertIsNot(self.prov._provData, {})

    def testGetDataNodes(self):
        df = self.prov.getDataNodes()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 9)

if __name__ == "__main__":
    unittest.main(exit = False)

'''
import pandas as pd
from parse import Parser

prov = Parser("tests/test.json")
'''