from numpy.lib.arraysetops import isin
import pandas as pd
import numpy as np
import webbrowser
import requests
import json
import sys
import re
from .ProvParser import Parser
from .ProvGrapher import Grapher
from pdb import set_trace as bp


class Explorer:

    # This class uses the information created from parsing provenance
    def __init__(self, filepath):
        self.prov = Parser(filepath)
        self.graph = Grapher(self.prov)
        self._procDataEdges = self.prov.getProcData()


    # This function is a post-mortem type checker. Pass it a single variable name, or multiple variables seperated as commas 
    # Note this means to type check multiple variables, call like this typeCheck("foo", "bar") not typeCheck(["foo", "bar"])
    # TODO: for multiple, maybe we really ought to accept a list...
    # This function will return a tuple, the first entry is a return code, where 0 is success and 1 is failure. When successful, 
    # the second element will be a dictionary, where the key is the variable name and the value is a dataframe of that variables types
    # if onlyBool is true, it will check whether or not a variable had the same type and the value will instead be a boolean. True if it kept
    # its type, false it changed types. If the function failed for some reason, the second tuple element will be a list of possible variable 
    # names that it can type check.
    def typeCheck(self, *args, onlyBool = False):

        # This value indicates whether or not the function was able to 
        # succesfully query the variables or not. In the event it does not
        # and this value gets changes to 1, the return value is all 
        # the possible variables rather than the (incorrect) queried ones
        retCode = 0

        # Variable exist in the provenance information as 'Data'
        # or 'Snapshot' types from the data nodes.
        posVars = self.getUniqueVarNames()
        
        posArgs = []

        # Don't process variables that don't exist in the provenance
        for arg in args:
            if(arg in posVars):
                posArgs.append(arg)
        
        retVal = {}

        # If they didn't input any valid arguments change the status code
        # that lets the function caller know they are receiving the posVars
        if(len(posArgs) == 0):
            retCode = 1
            retVal = posVars
        else:
            for arg in posArgs:
                retVal[arg] = self._getVarTypes(arg)

                if(onlyBool):
                    if(len(set(retVal[arg]["varType"].values)) == 1):
                        retVal[arg] = True
                    else:
                        retVal[arg] = False
            

        return(retCode, retVal)
    
    # This is a helper function for the typeChecking function
    # It takes a variable name and creates a dictionary out of it
    # The keys of the dictionary correspond to columns of the data frame
    # that the typeChecking function returns
    def _getVarTypes(self, varName):

        #For this function data nodes are used for grabbing the scope and valType information
        dataNodes = self.prov.getDataNodes()

        # The proc data edges allow the program to find what procedure nodes
        # match with the data nodes that match with the passed variable
        procData = self.prov.getProcData()

        # The procedure nodes show what line the variable was assigned
        procNodes = self.prov.getProcNodes()

        # This separates out the data nodes that are only from the variable passed
        matchedData = dataNodes[dataNodes["name"] == varName]

        # This finds the procedure node labels that have an edge to the data nodes
        matchedProcLabels = procData[procData.entity.isin(matchedData["label"].values)]["activity"].values

        # This returns the procedure rows that have a connection to the data nodes
        matchedProcNodes = procNodes[procNodes.label.isin(matchedProcLabels)]

        # This dictionary has keys matching the columns for the final data frame
        retVal = []
        line = matchedProcNodes["startLine"].values
        scope = matchedData["scope"].values
        valTypes = matchedData["valType"].values

        for index in range(0, len(line)):
            dfRow = {}

            dfRow["line"] = line[index]
            dfRow["scope"] = scope[index]

            try:
                valType = json.loads(valTypes[index])
                dfRow["container"] = valType["container"]
                dfRow["dim"] = valType["dimension"]
                dfRow["varType"] = valType["type"][0]
            except ValueError:
                dfRow["container"] = None
                dfRow["dim"] = None
                dfRow["varType"] = valTypes[index]

            retVal.append(dfRow)
        
        cols = ["line", "varType", "container", "dim", "scope"]
        return(pd.DataFrame(retVal)[cols])


    # This function searches the provenance for an error message
    # If one exists, it grabs it and prints the lineage.
    # If they set stackoverflow to true it will find similar messages on 
    # stackover flow, print them, and if the user chooses one 
    # will open that page in on the webbrowser
    def errorTrace(self, stackOverflow = False):
        retVal = pd.DataFrame()

        returnCode = 0

        message = self._procesError()
        # If there are no errors than message will be 0
        if(len(message) > 0):
            # Grab the error from the numpy series since it is initally grabbed as
            # a single element numpy series.
            message = message[0]

            retVal = [message, self.lineage("error.msg")]
        else:
            returnCode = 1

        return(returnCode, retVal)

    def _procesError(self):
        dataNodes = self.prov.getDataNodes()

        # Grab any possible error messages
        return(dataNodes[dataNodes["name"] == "error.msg"]["value"].values)


    def errorSearch(self):
        message = self._procesError()[0]
        # If they choose to find similar messages using the stack exchange API
 
        # Error messages tend to follow the format of:
        # 'Personalized Info : more info 'personalized' info
        # The personalized info should be removed, so first grab all 
        # text after the colon
        messageParts = message.split(":")
        if(len(messageParts) == 2):
            del messageParts[0]
            message = ''.join(messageParts)

        # Big oof
        # This complicated mess of regex actually checks for 4 things (all inclusive):
        # Matches to characters surronded by quotes "dog"
        # Matches to characters surronded by escaped quotes \"dog\"
        # Matches to characters surronded by single quotes 'dog'
        # Matches to characters surronded by escaped quotes \'dog\'
        exp = "\\\"[^\"\r]*\\\"|\"[^\"\r]*\"|\'[^\"\r]*\'|\\\'[^\"\r]*\\\'"

        # This will remove all text between quotes since that information is what is personalized.
        message = re.sub(exp, "", message)
        language = self.prov.getEnvironment().loc["language"][0]

        # Call to this function passes the parsed message to the StackExchange API
        result = self._stackSearch(message, language)
        result = pd.DataFrame(result["items"])
        result = result.sort_values(by="score", ascending = False).head()
        result.index = range(len(result.index))
        return(message, result)

    # takes the result returned from error search with a choice given by the user
    def openStackSearch(self, result, choice):
        link = result.iloc[[choice - 1]]["link"].values[0]
        webbrowser.open(link)


    # This function will query stack overflow for what is passed to it 
    # in the argument 'query'
    def _stackSearch(self, query, tagged, order = "desc", sort = "votes"):
        request = ("http://api.stackexchange.com/2.2/search?" + 
         "order=" + order +
         "&sort=" + sort + 
         "&tagged=" + tagged + 
         "&intitle=" + query + 
         "&site=stackoverflow")

        rawResult = requests.get(request)

        if(rawResult.status_code != 200):
            sys.exit("Stackoverflow connection failed")

        return(json.loads(rawResult.content.decode(rawResult.encoding)))


    def flatten(self, toFlatten):
        for x in toFlatten:
            if hasattr(x, '__iter__') and not isinstance(x, str):
                for y in self.flatten(x):
                    yield y
            else:
                yield x

    # This function takes variable names as inputs and returns 
    # a list of data frames with the lineage information for the
    # variables passed. (Lineage being the other variables that
    # use the inputted variable or were used in the creation of the
    # inputted variable 
    def lineage(self, *args, forward = False):

        returnCode = 0
        
        # Variable exist in the provenance information as 'Data'
        # or 'Snapshot' types from the data nodes. Having all of 
        # the possible variables they could choose allows error
        # checking argument input
        posVars = self.prov.getDataNodes()
        posVars = posVars[posVars.type.isin(["Data", "Snapshot", "Exception"])]
        posVars = list(set(posVars['name']))
        
        posArgs = []

        # Flattens the arguments in case a list of variables is passed.
        args = list(args)
        flat_list = self.flatten(args)

        # Don't process variables that don't exist in the provenance
        for arg in flat_list:
            if(arg in posVars):
                posArgs.append(arg)
        
        retVal = []

        # Inform the user if they either passed no variables
        # or if they passed variables not present. Return value of 
        # 1 means that possible variables have been returned 
        if(len(posArgs) == 0):
            returnCode = 1
            retVal = posVars
        else:
            # Process the lineage for each variable they passed and then return it
            for result in posArgs:
                retVal.append(self._grabLineage(result, forward)[["scriptNum", "startLine", "name"]])

        return(returnCode, retVal)

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
            retVal = pd.concat([retVal, procNodes.loc[procNodes["label"] == match, ["scriptNum", "startLine", "name", "label"]]])

        # Reindex rows for clarity 
        retVal.index = range(len(retVal.index))
        
        retVal["startLine"] = retVal["startLine"].replace("NA", np.nan)
        retVal = retVal.sort_values(by=["startLine"])

        return(retVal)

    # This function returns information about the values of variables
    # given a line from the program. It can either return all of the
    # variables referenced on a line, or the state of the entire execution
    # at the when the line was finished executing
    def fromLine(self, *args, state = False):
        returnCode = 0

        # The procedure nodes store the line numbers, grab only 
        # operations to avoid NA values such as from start and end nodes
        procNodes = self.prov.getProcNodes()
        self._procNodes = procNodes.loc[procNodes["type"].isin(["Operation", "Start"])]

        # Cannot display the result of a file write in code so take it out
        dataNodes = self.prov.getDataNodes()
        fileDelete = list(dataNodes.loc[dataNodes["type"] == "File"]["label"])
        
        self._dataNodes = dataNodes.loc[dataNodes["type"] != "File"]
        
        # Data to procedure edges show which data nodes are used during this procedure
        dataProcEdges = self.prov.getDataProc()

        self._dataProcEdges = dataProcEdges[~dataProcEdges['entity'].isin(fileDelete)]

        # The start line has the lines needed when debugging, check for all the arguments
        # they passed to make sure they are possible lines
        posLines = list(self._procNodes["startLine"])
        posLines = list(filter(lambda a: a != 'NA', posLines))
        args = pd.Series(args)
        args = list(args[args.isin(posLines)].values)

        retVals = []

        if (len(args) == 0):
            returnCode = 1
        else:
            # Process each line one at a time
            for arg in args:
                retVals.append(self._grabLine(arg, state))

        return(returnCode, retVals)
    
    # This function is a helper function to the fromLine function. It has two parts,
    # the first is dependent on whether the user is looking for variables from a single 
    # line or up to that point in execution. If the user is looking for variables from a 
    # single line then all associated 
    def _grabLine(self, lineNumber, state):
        
        # This variable will hold all of the nodes that are found to be relevant 
        # for the passed in line number. This list is passed to another helper function
        # that will grab the associated data nodes and construct a data frame from it
        nodes = []

        # When state is false, the user is looking for information regarding the values of the variables
        # on a single line of code. 
        if(state == False):
            
            # Find the procedure node labels from the line the user requested
            nodes = self._procNodes[self._procNodes["startLine"] == lineNumber]["label"].values
            
            # This structure will hold all of the nodes that have been referenced on a
            # line, *including the line itself*
            referencedNodes = np.array([])

            # Create a list of nodes those that are referenced on the line
            # by finding their corresponding data node (via data-to-proc edges)
            # and seeing if there's another proc node attached (via proc-to-data edges)
            for node in nodes:
                referencedEntity = self._dataProcEdges[self._dataProcEdges["activity"] == node]["entity"].values

                referencedNode = 'nan'      

                if (len(referencedEntity) > 0):
                    referencedNode = self._procDataEdges[self._procDataEdges["entity"].isin(referencedEntity)]["activity"].values
                    if(len(referencedNode) == 0):
                        referencedNode = referencedEntity
                
                referencedNodes = np.append(referencedNodes, referencedNode)
            
            # Combine the found nodes with the line's node
            referencedNodes = np.append(referencedNodes, nodes)
            # remove any blank nodes that may have been added in the search for 
            # referenced nodes 
            nodes = [x for x in referencedNodes if str(x) != 'nan']
            
        
        # If state == True that means they are looking for the state of execution up to this point 
        else:
            node = self._procNodes[self._procNodes["startLine"] == lineNumber]["label"].values[0]

            nodes = self._varsByNode(node)

        return(self._constructDataFrameFromNodes(nodes))

    # This function takes a list of nodes and will collect each data node related to them 
    # and construct them into a data frame. Used by fromLine and getVarsFromCurrentLocation 
    # in the ProvBrowser
    def _constructDataFrameFromNodes(self, nodes):
        retVal = []
        for node in nodes:
            if(node[0] == "p"):
                node = self._procDataEdges[self._procDataEdges["activity"] == node]["entity"].values
                if(len(node) is not 0):
                    node = node[0]
            retVal.append(self._processNode(node))
        cols = ["name", "value", "type", "container", "dimensions"]
        if(len(retVal) is 0):
            retVal = pd.DataFrame(columns=["name", "value", "type", "container", "dimensions"])
        else:
            retVal = pd.DataFrame(retVal)
            retVal = retVal.dropna()
        
        return(retVal[cols])

    # This helper function is used to find information about the node
    # passed to it. A row with the information is created and appended
    # to a data frame
    def _processNode(self, entity):

        # This dict will hold a single row of the later 
        # to be data frame, the dicts will be collected into a list
        # and converted into a data frame
        dfRow = {}

        # In case there is no data, initialize the row to NA
        dfRow["name"] = "NA" 
        dfRow["value"] = "NA" 
        dfRow["container"] = "NA" 
        dfRow["dimensions"] = "NA" 
        dfRow["type"] = "NA" 

        # If there is no entity then just assign the line to the name 
        # If there is an entity, grab it's info and populate the row
        if(len(entity) != 0):
            if(not hasattr(self, "_dataNodes")):
                dataNodes = self.prov.getDataNodes()
                self._dataNodes = dataNodes.loc[dataNodes["type"] != "File"]

            varInfo = self._dataNodes[self._dataNodes["label"] == entity]
            dfRow["name"] = varInfo["name"].values[0]
            dfRow["value"] = varInfo["value"].values[0]

            # R Functions do not have containers nor dimensions 
            if(varInfo["valType"].values[0] == "function"):
                dfRow["container"] = "NA"
                dfRow["dimensions"] = "NA"
                dfRow["type"] = "function"

            # If it's not an R function the type, container, and dimensions are
            # stored in a string as JSON
            else:
                valType = json.loads(varInfo["valType"].values[0])

                keys = valType.keys()

                for key in keys:
                    dfRow[key] = valType[key]
                '''
                dfRow["container"] = valType["container"]
                dfRow["dimensions"] = valType["dimension"][0]
                dfRow["type"] = valType["type"][0]
                '''
        else:
            dfRow["name"] = np.nan

        return(dfRow)

    # This function gathers all variables used in a procedure 
    # based on the node. Should always be passed a proc node.
    # returns a dataframe of data nodes
    # Used by fromLine and getVarsFromCurrentLocation in the Browser
    def _varsByNode(self, node):

        entity = self._procDataEdges[self._procDataEdges["activity"] == node]["entity"]
        if(len(entity) is not 0):
            entity = entity.values[0]
        while (len(entity) is 0):

            # Grab the procedure nodes and procedure data edges so
            # we can 'walk backward' through execution and grab the nodes
            # previous to our current ones

            procNodes = self.prov.getProcNodes()
            allProcNodes = procNodes.loc[procNodes["type"].isin(["Operation", "Start"])]
            allProcData = self.prov.getProcData()

            # Currently the indices are set to the labels, reindex them to 
            # ints so we can index through 
            allProcNodes.index = range(len(allProcNodes.index))
            newNodeIndex = allProcNodes[allProcNodes["label"] == node].index
            if(len(newNodeIndex) == 0):
                break
            else:
                newNodeIndex = newNodeIndex.values[0] - 1
            node = allProcNodes.iloc[[newNodeIndex]]["label"].values[0]
            entity = allProcData[allProcData["activity"] == node]["entity"]

            if(len(entity) is not 0):
                entity = entity.values[0]

            if(newNodeIndex == 0 and len(entity) == 0):
                break
        
        if(len(entity) is not 0):
            dataNodes = self.prov.getDataNodes()
            dataNodes = dataNodes.loc[dataNodes["type"] != "File"]

            dataNodes.index = range(len(dataNodes.index))
            rowNum = dataNodes[dataNodes["label"] == entity].index.values[0]
            nodes = dataNodes.iloc[:rowNum + 1]["label"].values

            # Account for duplicates by removing all but the tail
            nodeNames = dataNodes[dataNodes["label"].isin(nodes)]["name"].values
            tempDf = pd.DataFrame({"nodes":nodes, "names":nodeNames})
            nodes = tempDf.drop_duplicates(subset=["names"], keep="last")["nodes"].values
        else:
            nodes = []

        return(nodes)

    # This function will provide the procedure node where a data node was generated. 
    # Requires a data node label and returns a single dataframe row from procedure nodes
    def getProcedureFromData(self, data_node):
        procNodes = self.prov.getProcNodes()
        procToData = self.prov.getProcData()
        procNodeLabel = procToData.loc[procToData["entity"] == data_node]["activity"].values[0]
        procNode = procNodes.loc[procNodes["label"] == procNodeLabel]
        return(procNode)

    # This function will provide the data node a proc node generated. 
    # Requires a proc node label and returns a dataframe of data nodes
    # that are the nodes the procedure created
    # Otherwise if the proc node created no datanodes will return None
    def getDataFromProcedure(self, proc_node):
        dataNodes = self.prov.getDataNodes()
        procToData = self.prov.getProcData()
        dataNodeLabel = procToData.loc[procToData["activity"] == proc_node]["entity"].values
        
        if(len(dataNodeLabel) != 0):
            dataNodeList = dataNodes.loc[dataNodes["label"].isin(dataNodeLabel)]
        else:
            dataNodeList = None
        return(dataNodeList)

    # This function takes a variable name and returns that variables life cycles. 
    # Life cycles in this context are groups of instances of a single variable in 
    # the code where the variable was used to determine its own value. 
    # For example, the following code has two life cycles.
    # foo <- 5
    # foo <- 5 + foo
    # foo <- 10 * foo
    # foo <- "hello"
    # foo <- c(foo, "world")
    # the first life cycle is the first 3 instances, and the second life cycle is the last two lines
    # This function will return a list of dataframes. Each element in the list is a single life cycle, 
    # so the length of the list is the number of life cycles. Each dataframe is simple a subset of the 
    # entire data node data frame, except only the rows corresponding to that particular life cycle.
    def getVarLifeCycles(self, var_name):
        # Need all data and procedure nodes to find life cycles
        dataNodes = self.prov.getDataNodes()
        procNodes = self.prov.getProcNodes()

        # Get only variables that have the name as the passed variable
        varNodes = dataNodes.loc[dataNodes["name"] == var_name]

        # we use the labels to match with the correct rows in dataNodes dataframe
        varLabels = varNodes["label"].to_numpy()

        # Starting from the first node, we will track lineage forward in a script
        initialLabel = varNodes.iloc[0]["label"]

        # This is the final return value, a list of dataframes. The length of this
        # list is the number of lifeCycles for a variable
        lifeCycles = []

        # This loop will keep executing so long as there are still life cycles to be found
        # Each iteration will subset out the life cycles discovered, when there are no more
        # labels, that means all cycles have been found.
        while(len(varLabels) > 0):
            # collect the forward lineage of all related procedure nodes from this particular data node
            lineageProcs = self.getNodeLifeCycle(initialLabel, procNodes)
            dataLineage = []
            for node in lineageProcs:
                dataRow = self.getDataFromProcedure(node)
                if(dataRow is not None):
                    dataLineage.append(dataRow["label"].to_numpy())
            
            # Collect all the data nodes that were generated from proc nodes in this particular data node's forward lineage
            #dataLineage = np.concatenate([self.getDataFromProcedure(node)["label"].to_numpy() for node in lineageProcs])
            dataLineage = np.concatenate(dataLineage)

            # Mask is used to subset out the life cycle, and then remove life cycle by subsetting the negation of the mask
            cycle_mask = np.isin(varLabels, dataLineage)
            lifeCycles.append(dataNodes[np.isin(dataNodes["label"].to_numpy(),  varLabels[cycle_mask])])
            varLabels = varLabels[~cycle_mask]

            # Reset the initialLabel. If the length is 0, just break, as grabbing initial value will throw error
            if(len(varLabels) > 0):
                initialLabel = varLabels[0]
            else:
                break
            
        return(lifeCycles)


    # This function returns all unique variable names used in a script
    def getUniqueVarNames(self):
        posVars = self.prov.getDataNodes()
        retVal = []
        if("name" in posVars.columns):
            posVars = posVars[posVars.type.isin(["Data", "Snapshot"])]
            retVal = list(set(posVars['name']))
        return retVal

        # This function takes a data node, finds the procedure node that generated it, and then uses that proc node to find a
    # forward lineage of the data node that was passed in as a label. Returns an np array of procedure nodes.
    def getNodeLifeCycle(self, initialLabel, procNodes):

        initialNode = self.getProcedureFromData(initialLabel)["label"].to_numpy()[0]
        lineage_df = self._processLabel(initialLabel, procNodes, forward=True)
        if("label" not in lineage_df.columns):
            lineageProcs = [initialNode]
        else:
            lineageProcs = [initialNode] + list(self._processLabel(initialLabel, procNodes, forward=True)["label"].to_numpy())
        return(lineageProcs)