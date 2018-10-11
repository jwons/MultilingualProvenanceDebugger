import unittest
from parse import Parser

class TestProvParser(unittest.TestCase):

    def setUp(self):
        self.prov = Parser("tests/test.json")
    
    def testConstruction(self):
        self.assertIsNot(self.prov._provElements, {})
        self.assertIsNot(self.prov._provData, {})

    def testGetDataNodes(self):
        pass



if __name__ == "__main__":
    unittest.main(exit = False)