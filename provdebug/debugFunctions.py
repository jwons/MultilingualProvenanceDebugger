import pandas as pd
import numpy as np
import json
import re
from .Parse import Parser
from .Graph import Grapher

class ProvDebug:

    # This class uses the information created from parsing provenance
    def __init__(self, filepath):
        self.prov = Parser(filepath)
        self.graph = Grapher(self.prov)

    # This function takes variable names as inputs and returns 
    # a list of data frames with the lineage information for the
    # variables passed. (Lineage being the other variables that
    # use the inputted variable or were used in the creation of the
    # inputted variable 
    def lineage(self, *args, forward = False):

        # Variable exist in the provenance information as 'Data'
        # or 'Snapshot' types from the data nodes. Having all of 
        # the possible variables they could choose allows error
        # checking argument input
        posVars = self.prov.getDataNodes()
        posVars = posVars[posVars.type.isin(["Data", "Snapshot"])]
        posVars = list(set(posVars['name']))
        
        posArgs = []

        # Don't process variables that don't exist in the provenance
        for arg in args:
            if(arg in posVars):
                posArgs.append(arg)
        
        retVal = []

        # Inform the user if they either passed no variables
        # or if they passed variables not present
        if(len(posArgs) == 0):
            print("No variables were passed that matched variables from provenance.")
            print("Possible variables have been returned instead.")
            retVal = posVars
        else:
            # Process the lineage for each variable they passed and then return it
            for result in posArgs:
                retVal.append(self._grabLineage(result, forward))

        return(retVal)

    # This is a helper function for the lineage function
    def _grabLineage(self, result, forward):

        # The variables and information about individual lines are needed for the lineage
        dataNodes = self.prov.getDataNodes()
        procNodes = self.prov.getProcNodes()

        nodeLabel = ""

        # The node label changes depending on whether or no the lineage
        # is going forward or backward. 
        if(not forward):
            nodeLabel = list(dataNodes.loc[dataNodes["name"] == result].tail(1).index)[0]
        else:
            nodeLabel = list(dataNodes.loc[dataNodes["name"] == result].head(1).index)[0]

        return(self._processLabel(nodeLabel, procNodes, forward))

    # This is a helper function for processing labels from nodes
    # Currently used by lineage (and may by warning trace in the future)
    def _processLabel(self, nodeLabel, procNodes, forward):
        lineage = self.graph.getLineage(nodeLabel, forward)

        # This expression finds a string that starts with a 'p'
        # and then has some digits (of variable length), and then ends 
        regex = "^p\\d+$"

        # Return all of the matches from the regex, this allows us to 
        # separate the procedure nodes from the data nodes returned from the graph
        matches = [string for string in lineage if re.match(regex,string)]

        # The name has the (snippet of) code from a line, the startline is where the code begins
        retVal = pd.DataFrame(columns = ["scriptNum", "startLine", "name"])

        # Continually append rows for each procedure node returned from the graph search
        for match in matches:
            retVal = pd.concat([retVal, procNodes.loc[procNodes["label"] == match, ["scriptNum", "startLine", "name"]]])

        # Reindex rows for clarity 
        retVal.index = range(len(retVal.index))
        
        retVal["startLine"] = retVal["startLine"].replace("NA", np.nan)
        retVal = retVal.sort_values(by=["startLine"])

        return(retVal)

    # This function returns information about the values of variables
    # given a line from the program. It can either return all of the
    # variables referenced on a line, or the state of the entire execution
    # at the when the line was finihsed executing
    def fromLine(self, *args, state = False):

        # The procedure nodes store the line numbers, grab only 
        # operations to avoid NA values such as from start and end nodes
        procNodes = self.prov.getProcNodes()
        self._procNodes = procNodes.loc[procNodes["type"] == "Operation"]

        # The data edges are needed to grab vales from variables later on
        self._procDataEdges = self.prov.getProcData()

        # Cannot display the result of a file write in code so take it out
        dataNodes = self.prov.getDataNodes()
        fileDelete = list(dataNodes.loc[dataNodes["type"] == "File"]["label"])
        
        self._dataNodes = dataNodes.loc[dataNodes["type"] != "File"]
        
        dataProcEdges = self.prov.getDataProc()

        self._dataProcEdges = dataProcEdges[~dataProcEdges['entity'].isin(fileDelete)]

        # The start line has the lines needed when debugging, check for all the arguments
        # they passed to make sure they are possible lines
        posLines = list(self._procNodes["startLine"])
        args = pd.Series(args)
        args = list(args[args.isin(posLines)].values)

        retVals = []

        if (len(args) == 0):
            print("No valid arguments were passed")
        else:
            # Process each line one at a time
            for arg in args:
                retVals.append(self._grabLine(arg, state))

        return(retVals)
    
    def _grabLine(self, lineNumber, state):

        lineFrame = pd.DataFrame()

        if(state == False):
            nodes = self._procNodes[self._procNodes["startLine"] == lineNumber]["label"].values

            referencedNodes = np.array([])

            for node in nodes:
                referencedEntity = self._dataProcEdges[self._dataProcEdges["activity"] == node]["entity"].values

                referencedNode = 'nan'

                if (len(referencedEntity) > 0):
                    referencedNode = self._procDataEdges[self._procDataEdges["entity"].isin(referencedEntity)]["activity"].values
                    if(len(referencedNode) == 0):
                        referencedNode = referencedEntity
                
                referencedNodes = np.append(referencedNodes, referencedNode)
            
            referencedNodes = np.append(referencedNodes, nodes)
            referencedNodes = [x for x in referencedNodes if str(x) != 'nan']

            retVal = []

            for node in referencedNodes:
                retVal.append(self._processNode(node))
            #pd.DataFrame(columns = ["index", "name", "value", "container", "dimensions", "type"])
            retVal = pd.DataFrame(retVal)

            return(retVal)

    # This helper function is used to find information about the node
    # passed to it. A row with the information is created and appended
    # to a data frame
    def _processNode(self, node):
        if(node[0] == "p"): #Called by reference
            entity = self._procDataEdges[self._procDataEdges["activity"] == node]["entity"].values[0]

        dfRow = {}

        dfRow["name"] = "NA" 
        dfRow["value"] = "NA" 
        dfRow["container"] = "NA" 
        dfRow["dimensions"] = "NA" 
        dfRow["type"] = "NA" 

        if(len(entity) != 0):
            varInfo = self._dataNodes[self._dataNodes["label"] == entity]

            dfRow["name"] = varInfo["name"].values[0]
            dfRow["value"] = varInfo["value"].values[0]
            if(varInfo["valType"][0] == "function"):
                dfRow["container"] = "NA"
                dfRow["dimensions"] = "NA"
                dfRow["type"] = "function"
            else:
                valType = json.loads(varInfo["valType"][0])

                dfRow["container"] = valType["container"]
                dfRow["dimensions"] = valType["dimension"][0]
                dfRow["type"] = valType["type"][0]
        else:
            dfRow["name"] = self._procNodes[self._procNodes["label"] == node]["name"]

        return(dfRow)