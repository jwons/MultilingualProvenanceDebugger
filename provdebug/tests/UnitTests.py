import unittest
import pandas as pd
import provdebug as pvd

class TestProvParser(unittest.TestCase):

    def setUp(self):
        self.prov = pvd.Parser("provdebug/tests/test.json")
    
    def testConstruction(self):
        self.assertTrue(hasattr(self.prov, '_provElements'))
        self.assertTrue(hasattr(self.prov, '_provData'))

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

class TestProvGrapher(unittest.TestCase):

    def setUp(self):
        prov = pvd.Parser("provdebug/tests/test.json")
        self.graph = pvd.Grapher(prov)
    
    def testConstruction(self):
        self.assertTrue(hasattr(self.graph, '_nodes'))
        self.assertTrue(hasattr(self.graph, '_graph'))

    def testLineage(self):
        self.assertEqual(self.graph.getLineage("d6"), ['d6', 'p8', 'd5', 'p6', 'd2', 'p3', 'd4', 'p5'])
        self.assertEqual(self.graph.getLineage("d6", backward=False), ['d6', 'p9', 'd7'])


if __name__ == "__main__":
    unittest.main(exit=False)