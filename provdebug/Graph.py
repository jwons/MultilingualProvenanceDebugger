import networkx as nx
import pandas as pd
import numpy as np
from .Parse import Parser

class Grapher:

    def __init__(self, prov):
        
        # The nodes of the graph will be the nodes from the provenance
        # This grapher needs to track all the edges between data and procedures
        self._nodes = list(prov.getProcNodes()["label"]) + list(prov.getDataNodes()["label"])

        # In the provenance the edges of the graph are stored.
        # They are labeled with the types of nodes they are, 
        # it is *necessary* to rename them as next in the code 
        # when they are concatenated the activities/entities will 
        # all be placed on the same column, when in reality there 
        # will be both activities and entities on both sides. So here
        # the columns are renamed to be more accurate and prevent that. 
        procData = prov.getProcData().rename(columns={"activity": "from", "entity":"to"})
        dataProc = prov.getDataProc().rename(columns={"entity": "from", "activity":"to"})

        edges = pd.concat([procData, dataProc], sort = True)
        
        # This creates an all zero dataframe of the corrrect proportions that
        # will have the connections assinged as "1" next 
        df = pd.DataFrame(0, index = self._nodes, columns= self._nodes)

        # Mark the connections using the value of 1
        for edge in zip(edges["from"], edges["to"]):
            df.loc[edge[1], edge[0]] = 1

        # Create the graph save it to the class
        self._graph = nx.from_numpy_matrix(df.values, create_using = nx.DiGraph())

    # This function is used to generate a list of the nodes that a singular
    # node is connected to. The user can choose to search for connections forward
    # or backward.
    def getLineage(self, nodeID, forward = False):

        # The traversal algorithm is dependent on the index value of
        # the chosen node. 
        nodeIndex = self._nodes.index(nodeID)

        # Finding the connections forward vs backward in the script is 
        # as simple as reversing the edges in the graph. The graph is 
        # stored with the edges pointing for backward connections.
        if(not forward):
            nodeIndices = list(nx.dfs_preorder_nodes(self._graph, nodeIndex))
        else:
            nodeIndices = list(nx.dfs_preorder_nodes(self._graph.reverse(), nodeIndex))
        
        # The traversal algorithm returns the indices of the nodes from the graph
        # this finds them, and then creates the return value, the list of node connections.
        lineage = []
        for node in nodeIndices:
            lineage.append(self._nodes[node])

        return(lineage)
