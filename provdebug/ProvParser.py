import json
import re
import pandas as pd

class Parser:

    # Constructor takes a filepath to a provenance file and reads in 
    # the information into memory
    def __init__(self, inputProv, isFile = True):
        prov = ""
        # holds the dictionary of provenance
        self._provData = {}

        # Holds a dictionary of data frames where each data frame is an 
        # "element" of the provenance. e.g procedure nodes, data nodes, etc.
        self._provElements = {}


        self._provEdges = None
        
        # before the json can be converted into a Pythonic structure
        # it has to be 'cleaned.' prefixes and comments are removed
        self.provLines = []


        if(isFile):
            with open(inputProv) as provJson:
                provLines = provJson.readlines()
        else:
            provLines = inputProv.split("\n")

        for line in provLines:
            if("//" in line):
                provLines.remove(line)

        prov = "".join(provLines)
        prov = prov.replace("rdt:", "")
        prov = prov.replace("prov:", "")
        prov = json.loads(prov)

        

        # Unlist the nested dictionary by one level. This 
        # way we have a 'master list' of provenance nodes and edges
        for provKey in prov:
            for provElement in prov[provKey]:
                self._provData[provElement] = prov[provKey][provElement]

        # Here start building up the parsed dic that will be queried by getter functions
        provChars = {"procNodes":"p", "dataNodes":"d", "funcNodes":"f",
                    "procProcEdges":"pp", "procDataEdges":"pd", "dataProcEdges":"dp",
                    "funcProcEdges":"fp", "funcLibEdges":"m", "agents":"a"}

        for key in provChars:
            self._provElements[key] = self._parseGeneral(provChars[key])

        # Add the environment prov data
        d = dict((k, self._provData[k]) for k in ["environment"])
        self._provElements["environment"] = pd.DataFrame(data = d)

        # Add the libraries used 
        d = self._parseGeneral("l")
        self._provElements["libraries"] = d[["name", "version"]]

        # Add the scripts sourced 
        d = dict((k, self._provData["environment"][k]) for k in ["sourcedScripts", "sourcedScriptTimeStamps"])
        self._provElements["scripts"] = pd.DataFrame(data = d, index = range(0, len(d["sourcedScripts"])))

        procData = self.getProcData()
        dataProc = self.getDataProc()
        funcProc = self.getFuncProc()
        funcLib = self.getFuncLib()

        procData.rename(columns = {'activity':'source', 'entity':'target'}, inplace = True)
        dataProc.rename(columns = {'entity':'source', 'activity':'target'}, inplace = True)
        funcProc.rename(columns = {'entity':'source', 'activity':'target'}, inplace = True)
        funcProc.rename(columns = {'collection':'source', 'entity':'target'}, inplace = True)

        self._provEdges = pd.concat([procData, dataProc, funcProc, funcProc], axis=0)

        procNodes = self.getProcNodes()
        row_index = 0
        loop_nodes = []
        for index, row in procNodes.iterrows():
            if(row["type"] == "Start" and row["name"] == "for loop"):
                if(procNodes.iloc[[row_index - 1]]["type"].values[0] == "Start"):
                    previousNode = procNodes.iloc[[row_index - 1]]
                    endNode = procNodes.loc[
                        (procNodes["startLine"] == previousNode["startLine"].values[0]) &
                        (procNodes["endLine"] == previousNode["endLine"].values[0]) & 
                        (procNodes["startCol"] == previousNode["startCol"].values[0]) &
                        (procNodes["endCol"] == previousNode["endCol"].values[0]) &
                        (procNodes["type"] == "Finish")]
                    loop_nodes.append((previousNode.index.values[0], endNode.index.values[0]))
            row_index += 1
        self.loop_nodes = loop_nodes


    # To process nodes/edges from the master list the same process can be used
    # for most of them. This function handles converting dicts to the necessary data frame.
    def _parseGeneral(self, requested):

        # regex matches when a string starts with the letter(s) requested and is followed
        # by a variable amount of digits, and the string ends after the digits
        regex = "^" + requested + "\\d+$"
        
        # finding all of the matching keys using regex
        matches = [string for string in self._provData.keys() if re.match(regex,string)]
        
        # make a dict that can be converted into a data frame from those keys
        d = dict((k, self._provData[k]) for k in matches)

        retVal = pd.DataFrame(data = d).T

        labels = list(retVal.index)

        retVal["label"] = pd.Series(labels, index = retVal.index)

        return(retVal)

    # Access function to get any part of the parsed provenance
    def getProvInfo(self, requestedProv):
        df = self._provElements[requestedProv]
        try:
            df = df.iloc[df.index.str.extract(r'(\d+)', expand=False).astype(int).argsort()]
        except ValueError:
            pass

        return(df)

    def getEnvironment(self):
        return(self.getProvInfo("environment"))

    def getLibs(self):
        return(self.getProvInfo("libraries"))

    def getScripts(self):
        return(self.getProvInfo("scripts"))

    def getProcNodes(self):
        return(self.getProvInfo("procNodes"))

    def getDataNodes(self):
        return(self.getProvInfo("dataNodes"))

    def getFuncNodes(self):
        return(self.getProvInfo("funcNodes"))

    def getProcProc(self):
        return(self.getProvInfo("procProcEdges"))

    def getDataProc(self):
        return(self.getProvInfo("dataProcEdges"))

    def getProcData(self):
        return(self.getProvInfo("procDataEdges"))

    def getFuncProc(self):
        return(self.getProvInfo("funcProcEdges"))

    def getFuncLib(self):
        return(self.getProvInfo("funcLibEdges"))


    # This function returns the files that were read in to the script.
    # It does this by checking the data nodes of the type "File",
    # with data to procedure edges. 
    def getInputFiles(self):
        dataNodes = self.getDataNodes()

        dataNodes = dataNodes[dataNodes.type.isin(["File"])]
        if(len(dataNodes.index) != 0):
            dataProc = list(self.getDataProc()["entity"])
            dataNodes = dataNodes[dataNodes.index.isin(dataProc)]

        return(dataNodes[["name", "location", "timestamp"]])
    
    # This function returns the files that were read in to the script.
    # It does this by checking the data nodes of the type "File",
    # with procedure to data edges. 
    def getOutputFiles(self):
        dataNodes = self.getDataNodes()

        dataNodes = dataNodes[dataNodes.type.isin(["File"])]
        if(len(dataNodes.index) != 0):
            procData = list(self.getProcData()["entity"])
            dataNodes = dataNodes[dataNodes.index.isin(procData)]

        return(dataNodes[["name", "location", "timestamp"]])

    def _getEdgeRelation(self, procID, from_column, to_column):
        return(list(self._provEdges[self._provEdges[from_column] == procID][to_column].values))


    def getParentIDs(self, childID):
        return(self._getEdgeRelation(childID, "target", "source"))

    def getChildIDs(self, childID):
        return(self._getEdgeRelation(childID, "source", "target"))
    
    def getLoopNodes(self):
        return(self.loop_nodes)