import pandas as pd
import numpy as np
import re
from .Parse import Parser
from .Graph import Grapher

class ProvDebug:

    def __init__(self, filepath):
        self.prov = Parser(filepath)
        self.graph = Grapher(self.prov)

    def lineage(self, *args, forward = False):
        posVars = self.prov.getDataNodes()
        posVars = posVars[posVars.type.isin(["Data", "Snapshot"])]
        posVars = list(set(posVars['name']))
        
        posArgs = []

        for arg in args:
            if(arg in posVars):
                posArgs.append(arg)
        
        retVal = []

        if(len(posArgs) == 0):
            print("No variables were passed that matched variables from provenance.")
            print("Possible variables have been returned instead.")
            retVal = posVars
        else:
            for result in posArgs:
                retVal.append(self._grabLineage(result, forward))

        return(retVal)

    def _grabLineage(self, result, forward):
        dataNodes = self.prov.getDataNodes()
        procNodes = self.prov.getProcNodes()

        nodeLabel = ""

        if(not forward):
            nodeLabel = list(dataNodes.loc[dataNodes["name"] == result].tail(1).index)[0]
        else:
            nodeLabel = list(dataNodes.loc[dataNodes["name"] == result].head(1).index)[0]

        return(self._processLabel(nodeLabel, procNodes, forward))

    def _processLabel(self, nodeLabel, procNodes, forward):
        lineage = self.graph.getLineage(nodeLabel, forward)

        # This expression finds a string that starts with a 'p'
        # and then has some digits (of variable length), and then ends 
        regex = "^p\\d+$"

        matches = [string for string in lineage if re.match(regex,string)]

        retVal = pd.DataFrame(columns = ["scriptNum", "startLine", "name"])

        for match in matches:
            retVal = pd.concat([retVal, procNodes.loc[procNodes["label"] == match, ["scriptNum", "startLine", "name"]]])

        retVal.index = range(len(retVal.index))

        retVal["startLine"] = retVal["startLine"].replace("NA", np.nan)
        retVal = retVal.sort_values(by=["startLine"])

        return(retVal)

'''
    def debugFromLine(self, *args, state = False):
        procNodes = self.prov.getProcNodes()
        self._procNodes = procNodes.loc[procNodes["type"] == "Operation"]

        self._procDataEdges = self.prov.getProcData()

        dataNodes = self.prov.getDataNodes()
        fileDelete = list(dataNodes.loc[dataNodes["type"] == "File"]["label"])
        
        self._dataNodes = dataNodes.loc[dataNodes["type"] != "File"]
        
        dataProcEdges = self.prov.getDataProc()

        self._dataProcEdges = dataProcEdges[~dataProcEdges['entity'].isin(fileDelete)]



        posLines = list(self._procNodes["startLine"])

        for arg in args:
            if(arg in posLines):
                print(arg + " is a possible line")
        '''
        









