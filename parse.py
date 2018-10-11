import json
import re
import pandas as pd

class Parser:

    # holds the dictionary of provenance
    _provData = {}
    
    #Holds a dictionary of data frames where each data frame is an 
    # "element" of the provenance. e.g procedure nodes, data nodes, etc.
    _provElements = {}

    # Constructor takes a filepath to a provenance file and reads in 
    # the information into memory
    def __init__(self, filepath):
        prov = ""
        
        # before the json can be converted into a Pythonic structure
        # it has to be 'cleaned.' prefixes and comments are removed
        with open(filepath) as provJson:
            provLines = []
            for line in provJson:
                if("//" not in line):
                    provLines.append(line)

            prov = ''.join(provLines)

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
        self._provElements["scripts"] = pd.DataFrame(data = d, index = range(0, len(d) - 1))

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

        return(pd.DataFrame(data = d).T)

    # Access function to get any part of the parsed provenance
    def getProvInfo(self, requestedProv):
        return(self._provElements[requestedProv])

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
        return(self.getProvInfo("procDataEdges"))

    def getProcData(self):
        return(self.getProvInfo("procDataEdges"))

    def getFuncProc(self):
        return(self.getProvInfo("funcProcEdges"))
