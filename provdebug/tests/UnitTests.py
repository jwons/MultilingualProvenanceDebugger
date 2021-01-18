import unittest
import collections
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
        self.assertEqual(len(list(df.columns.values)), 10)
    
    def testGetProcNodes(self):
        df = self.prov.getProcNodes()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 9)

    def testGetFuncNodes(self):
        df = self.prov.getFuncNodes()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 2)

    def testGetProcProc(self):
        df = self.prov.getProcProc()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 3)

    def testGetProcData(self):
        df = self.prov.getProcData()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 3)

    def testGetDataProc(self):
        df = self.prov.getDataProc()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 3)

    def testGetFuncProc(self):
        df = self.prov.getFuncProc()
        self.assertTrue(type(df) == pd.DataFrame)
        self.assertEqual(len(list(df.columns.values)), 3)

class TestProvGrapher(unittest.TestCase):

    def setUp(self):
        prov = pvd.Parser("provdebug/tests/test.json")
        self.graph = pvd.Grapher(prov)
    
    def testConstruction(self):
        self.assertTrue(hasattr(self.graph, '_nodes'))
        self.assertTrue(hasattr(self.graph, '_graph'))

    def testLineage(self):
        self.assertEqual(self.graph.getLineage("d6"), ['d6', 'p8', 'd5', 'p6', 'd2', 'p3', 'd4', 'p5'])
        self.assertEqual(self.graph.getLineage("d6", forward=True), ['d6', 'p9', 'd7'])

class TestProvDebugger(unittest.TestCase):

    def setUp(self):
        self.pvdebug = pvd.Explorer("provdebug/tests/test.json")
    
    def testTypeCheckNoArgs(self):
        returnCode, returnValue = self.pvdebug.typeCheck()
        self.assertEqual(returnCode, 1)
        self.assertEqual(len(returnValue), 4)
        self.assertTrue(collections.Counter(returnValue) == collections.Counter(['total.heads', 'probs', 'coin.flips', 'b']))

    def testTypeCheckArg(self):
        returnCode, returnValue = self.pvdebug.typeCheck("b")
        self.assertEqual(returnCode, 0)
        self.assertEqual(returnValue["b"]["varType"][0], "function")

    def testBlankLineage(self):
        returnCode, returnValue = self.pvdebug.lineage()
        self.assertEqual(returnCode, 1)
        self.assertTrue(collections.Counter(returnValue) == collections.Counter(['total.heads', 'probs', 'coin.flips', 'b']))

    #TODO Expand on this one
    def testSpecificLineage(self):
        returnCode, returnValue = self.pvdebug.lineage('total.heads')
        self.assertEqual(returnCode, 0)

    def testBlankFromLine(self):
        returnCode, returnValue = self.pvdebug.fromLine()
        self.assertEqual(returnCode, 1)
    
    def testSpecificFromLine(self):
        returnCode, returnValue = self.pvdebug.fromLine(3)
        self.assertEqual(returnCode, 0)
        self.assertEqual(returnValue[0]["name"][0], "b")


if __name__ == "__main__":
    unittest.main(exit=False)