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
        lastScope = [0]

        self._scopeStack = []

        procNodes = self.debugger.prov.getProcNodes()

        for index, row in procNodes.iterrows():
            print(index)
            '''
            if(row['type'] == "Start"):
                self._scopeStack.append([])
                self._scopeStack[self._currentScope].append({"row":row, "scopeChange":numOfScopes + 1})
                lastScope.append(self._currentScope)
                numOfScopes += 1
                self._currentScope = numOfScopes
            elif(row["type"] == "Finish"):
                self._scopeStack[self._currentScope].append({"row":row, "scopeChange":lastScope[-1]})
                self._currentScope = lastScope[-1]
                del lastScope[-1]
            else:
                self._scopeStack[self._currentScope].append({"row":row, "scopeChange":self._currentScope})  
            '''            
            

        # This variable keeps track of the objects place in the simulated execution
        self.currentNode = self.procProcEdges.loc["pp1"]["informant"]

    # This function can be called to advance the simulated execution by a single 
    # procedure. By default it should not step into anything such as loops, sourced
    # scripts, or other control structures. If it's called already at the end of the 
    # nodes, it will return 1 rather than 0 and keep the same node number. 
    def nextNode(self):
        oldNode = self.currentNode
        returnCode = 0

        try:
            self.currentNode = self.procProcEdges[self.procProcEdges["informant"] == oldNode]["informed"][0]
        except IndexError:
            returnCode = 1

        return returnCode

    # This function can be called to back up the simulated execution by a single 
    # procedure. By default it should not step into anything such as loops, sourced
    # scripts, or other control structures. If it's called already at the start of the 
    # nodes, it will return 1 rather than 0 and keep the same node number.
    def previousNode(self):
        oldNode = self.currentNode
        returnCode = 0

        try:
            self.currentNode = self.procProcEdges[self.procProcEdges["informed"] == oldNode]["informant"][0]
        except IndexError:
            returnCode = 1

        return returnCode


        



    
