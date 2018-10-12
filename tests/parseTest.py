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
    
    def testGetProcNodes(self):
        df = self.prov.getProcNodes()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 8)

    def testGetFuncNodes(self):
        df = self.prov.getFuncNodes()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 1)

    def testGetProcProc(self):
        df = self.prov.getProcProc()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 2)

    def testGetProcData(self):
        df = self.prov.getProcData()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 2)

    def testGetDataProc(self):
        df = self.prov.getDataProc()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 2)

    def testGetFuncProc(self):
        df = self.prov.getFuncProc()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 2)

if __name__ == "__main__":
    unittest.main(exit = False)

'''
import pandas as pd
from Parse import Parser

prov = Parser("tests/test.json")
'''