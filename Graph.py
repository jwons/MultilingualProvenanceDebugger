import networkx as nx
import pandas as pd
import numpy as np
from Parse import Parser

class Grapher:

    def __init__(self, prov):
        procData = prov.getProcData().rename(columns={"activity": "from", "entity":"to"})
        dataProc = prov.getDataProc().rename(columns={"entity": "from", "activity":"to"})

        edges = pd.concat([procData, dataProc], sort = True)

        self._nodes = list(prov.getProcNodes().index) + list(prov.getDataNodes().index)

        df = pd.DataFrame(0, index = self._nodes, columns= self._nodes)

        for edge in zip(edges["from"], edges["to"]):
            df.loc[edge[1], edge[0]] = 1

        self._graph = nx.from_numpy_matrix(df.values, create_using = nx.DiGraph())

    def getLineage(self, nodeID, backward = True):
        nodeIndex = self._nodes.index(nodeID)

        if(backward):
            nodeIndices = list(nx.dfs_preorder_nodes(self._graph, nodeIndex))
        else:
            nodeIndices = list(nx.dfs_preorder_nodes(self._graph.reverse(), nodeIndex))
        
        lineage = []
        for node in nodeIndices:
            lineage.append(self._nodes[node])

        return(lineage)
