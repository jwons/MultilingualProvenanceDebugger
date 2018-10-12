from Parse import Parser
from Graph import Grapher

if __name__ == '__main__':
    prov = Parser('tests/test.json')
    graph = Grapher(prov)

    print("--------Provenance Information--------")
    print("###########################################################")
    print("Program's computing environment:")
    print(prov.getEnvironment())
    print("###########################################################")
    print("Program's libraries")
    print(prov.getLibs())
    print("###########################################################")
    print("Program's data nodes")
    print(prov.getDataNodes())
    print("###########################################################")
    print("Lineage information:")
    print("Lineage for 'd6'")
    print(graph.getLineage("d6"))
    print("Forward lineage for 'd6'")
    print(graph.getLineage("d6", backward=False))