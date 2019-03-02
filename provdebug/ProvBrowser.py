import os
import natsort
from .debugFunctions import ProvDebug

# This class uses prov.json file to reconstruct a past execution 
# and can walk forwards and backwards through it. This class is not 
# intended to be used as the direct interface to a user. Rather,
# an interface can be built on top of this class.

class ProvBrowser:

    # This constructor takes a prov.json filename as an argument 
    # to initialize the debugger object which will parse the json
    # using the Parser object
    def __init__(self, filename):
        self.debugger = ProvDebug(filename)

        # The debugger object has a parsing object in it that can be
        # used to query the environment node for the script name
        self.scriptName = os.path.basename(self.debugger.prov.getEnvironment().loc["script"][0])

        # The procedure to procedure edges are used to determine which 
        # will be the next node to advance to when a user prompts 
        self.procProcEdges = self.debugger.prov.getProcProc()

        # This variable keeps track of where the simulated execution is in terms of 
        # scope that is possible to step in and out of. It merely represents an index
        # to a list of procedure nodes
        self._currentScope = 0

        # These are used to keep track of positions when traveling
        # through the procedure nodes one at a time initially and 
        # organizing them into different scopes. 
        numOfScopes = 0
        lastScope = []

        # The scope stack will represent the different scopes that exist 
        # within the simulated execution. It is a list of lists, where the 
        # inner lists contain a dictionary with procedure nodes and possible scope changes
        self._scopeStack = []
        self._scopeStack.append([])

        procNodes = self.debugger.prov.getProcNodes()

        # This loop makes an initial iteration through all of the procedure 
        # nodes and organizes each one into its respective "scope"
        for index, row in procNodes.iterrows():
            
            # Start nodes indicate the possibility of a new scope could
            # be stepped into at this node. Therefore, when appending the 
            # node to the scopeStack, indicate with the scopeChange dict 
            # element that index value into the scopeStack could be traeversed 
            # to during the program reconstruction
            if(row['type'] == "Start"):
                self._scopeStack.append([])
                self._scopeStack[self._currentScope].append({"row":row, "scopeChange":numOfScopes + 1})
                lastScope.append(self._currentScope)
                numOfScopes += 1
                self._currentScope = numOfScopes
            # A finish node indicates that the last node will be where the 
            # reconstrucuted execution will leave the scope to traverse back to 
            # the one it was in previosuly 
            elif(row["type"] == "Finish"):
                self._scopeStack[self._currentScope][-1]["scopeChange"] = lastScope[-1]
                self._currentScope = lastScope[-1]
                #TODO This may be optional
                #self._scopeStack[self._currentScope].append({"row":row, "scopeChange":lastScope[-1]})
                del lastScope[-1]
            else:
                self._scopeStack[self._currentScope].append({"row":row, "scopeChange":self._currentScope})  

        # Reset to ensure simulated code will start at beginning
        self._currentScope = 0
        # This variable keeps track of the objects place in the simulated execution
        # self.currentNode = self.procProcEdges.loc["pp1"]["informant"]
        self.currentNodeIndex = 0

        self.positionStack = []

    # This function takes whatever node is currently selected and returns its 
    # script num, line number, and then either script name or code line
    def getCurrentNodeInfo(self):
        data = self._scopeStack[self._currentScope][self.currentNodeIndex]["row"]
        # If the script and line nums are NA it's the beginning of the script,
        # set to 0 for now 
        lineNum = data["startLine"]
        if(lineNum == "NA"):
            lineNum = "0"
        scriptNum = data["scriptNum"]
        if(scriptNum == "NA"):
            scriptNum = 0
        return('%s.%s. %s' %(scriptNum, lineNum, data["name"]))

    # This function sets the node information to be that of a node a single scope deeper, 
    # if possible. Otherwise it will just advance forward one node in the current scope
    def stepIn(self):
        # Check if the scope change stored in the dict points to a different scope than the current 
        # If it does the set all the current indexes to the next scope. Additionally, keep track 
        # of where the program entered to get back to it later.
        if(self._scopeStack[self._currentScope][self.currentNodeIndex]["scopeChange"] != self._currentScope):
            self.positionStack.append({"scope": self._currentScope, "node":self.currentNodeIndex})
            self._currentScope = self._scopeStack[self._currentScope][self.currentNodeIndex]["scopeChange"]
            self.currentNodeIndex = 0
        else:
            self.nextNode()
    
    def stepOut(self):
        if(len(self.positionStack) > 0):
            self.currentNodeIndex = self.positionStack[-1]["node"]
            self._currentScope = self.positionStack[-1]["scope"]
            del self.positionStack[-1]

    # This function can be called to advance the simulated execution by a single 
    # procedure. By default it should not step into anything such as loops, sourced
    # scripts, or other control structures. If it's called already at the end of the 
    # nodes, it will return 1 rather than 0 and keep the same node number. 
    def nextNode(self):

        if(self.currentNodeIndex + 1 < len(self._scopeStack[self._currentScope])):
            self.currentNodeIndex += 1
        elif(self.currentNodeIndex + 1 == len(self._scopeStack[self._currentScope]) and len(self.positionStack) > 0):
            self.stepOut()       

    # This function can be called to back up the simulated execution by a single 
    # procedure. By default it should not step into anything such as loops, sourced
    # scripts, or other control structures. If it's called already at the start of the 
    # nodes, it will return 1 rather than 0 and keep the same node number.
    def previousNode(self):

        if(self.currentNodeIndex - 1 > -1):
            self.currentNodeIndex -= 1
        elif(self.currentNodeIndex -1 == -1):
            self.stepOut()
    
    # This function lists all the variables that exist in the current point of execution
    def getVarsFromCurrentLocation(self):
        #self.debugger._varsByNode(self.)
        currentNode = self._scopeStack[self._currentScope][self.currentNodeIndex]["row"]["label"]

        df = self.debugger._constructDataFrameFromNodes(self.debugger._varsByNode(currentNode))

        retVal = list(df["name"])

        return(retVal)