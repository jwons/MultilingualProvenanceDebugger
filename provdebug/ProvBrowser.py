import os
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

        # This variable keeps track of the objects place in the simulated execution
        self.currentNode = self.procProcEdges.loc["pp1"]["informant"]

    def nextNode(self):
        oldNode = self.currentNode
        returnCode = 0

        try:
            self.currentNode = self.procProcEdges[self.procProcEdges["informant"] == oldNode]["informed"][0]
        except IndexError:
            returnCode = 1

        return returnCode

    def previousNode(self):
        oldNode = self.currentNode
        returnCode = 0

        try:
            self.currentNode = self.procProcEdges[self.procProcEdges["informed"] == oldNode]["informant"][0]
        except IndexError:
            returnCode = 1

        return returnCode


        



    
