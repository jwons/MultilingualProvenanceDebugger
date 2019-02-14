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

        self._currentScope = 0

        numOfScopes = 0
        lastScope = []

        self._scopeStack = []
        self._scopeStack.append([])

        procNodes = self.debugger.prov.getProcNodes()

        for index, row in procNodes.iterrows():
            
            if(row['type'] == "Start"):
                self._scopeStack.append([])
                self._scopeStack[self._currentScope].append({"row":row, "scopeChange":numOfScopes + 1})
                lastScope.append(self._currentScope)
                numOfScopes += 1
                self._currentScope = numOfScopes
            elif(row["type"] == "Finish"):
                self._scopeStack[self._currentScope][-1]["scopeChange"] = lastScope[-1]
                self._currentScope = lastScope[-1]
                #TODO This may be optional
                self._scopeStack[self._currentScope].append({"row":row, "scopeChange":lastScope[-1]})
                del lastScope[-1]
            else:
                self._scopeStack[self._currentScope].append({"row":row, "scopeChange":self._currentScope})  

        '''
        counter = 0
        for scope in self._scopeStack:
            print("Scope number: ", counter)
            for row in scope:
                print(row["row"]["label"], "| goes to:", row["scopeChange"])
            counter += 1
        '''

        # Reset to ensure simulated code will start at beginning
        self._currentScope = 0
        # This variable keeps track of the objects place in the simulated execution
        # self.currentNode = self.procProcEdges.loc["pp1"]["informant"]
        self.currentNodeIndex = 0

        self.positionStack = []

    def getCurrentNodeInfo(self):
        return(self._scopeStack[self._currentScope][self.currentNodeIndex]["row"])

    def stepIn(self):
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
    