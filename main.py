from parse import Parser

if __name__ == '__main__':
    prov = Parser('tests/test.json')

    provChars = ["procNodes", "dataNodes", "funcNodes",
                "procProcEdges", "procDataEdges", "dataProcEdges",
                "funcProcEdges", "funcLibEdges", "agents"]

    for provElement in provChars:
        print(prov.getProvInfo(provElement))

    