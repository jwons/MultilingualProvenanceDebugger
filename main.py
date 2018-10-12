from Parse import Parser
from Graph import Grapher

if __name__ == '__main__':
    prov = Parser('tests/test.json')
    graph = Grapher(prov)

    
    