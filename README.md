# Multilingual Provenance Debugger

A langugage - agnostic version of [provDebugR.](https://github.com/ProvTools/provDebugR/wiki)

For instructions on how to use the debugger visit the repository's [wiki](https://github.com/jwons/MultilingualProvenanceDebugger/wiki).

This debugger uses provenance information to reconstruct past-executions and allow users to explore them at their will. This tool will work with any program so long as it has provenance collected that follows [this format](https://github.com/End-to-end-provenance/ExtendedProvJson).

## Installation
To install as a package run `pip setup.py install` from the repo directory. 

If any dependency problems are found, the 
Python requirements are in requirements.txt so run `pip install -r requirements.txt`. 

## Current Features

### Debugging Features

**Command-Line Debugging:**
This functions similarly to standard command-line debuggers. A user will be able to step through a past execution as if it was currently being debugged. However, this will also have the added benefit of letting the user step backwards or forwards. Additionally, they can call some of the extra features the debugger has like checking a variable's lineage. 

**Lineage:**
A function that finds connections that variables have with each other and will return a variable's forward or backward connections.

**Error Tracing:** 
Error trace can be used to trace the lineage of an error message (if an error exists), returning the lines that led up to a script's stopping. It can also query Stack Overflow for similar errors and provide the user the option to open one of the similar questions in the browser.

**Type Checking:**
A function that can be used to examine how or whether or not a variable's type changes throughout the execution of a script.

**By Line Information:**
A function that can be used to examine the variables that exist in a script on a line-by-line basis. This function can be used in two ways, can either display all the variables and their values on a single line, or all variables that existed in the program's environment at a certain line number.

### Miscellaneous Features

**Provenance Parsing**
A python module exists within this package capable of parsing the prov.json files. It loads the different nodes and edges into pandas data frames. 

**Graph Conversion**
A python module exists within this package capable of using the information from the parsing module to create a network data structure using the networkx package. This structure is then used by the debugging class to find lineage of various provenance nodes.

## Explorer Functions

### typeCheck(*args, onlyBool = False)

This function is a post-mortem type checker. Pass it a single variable name, or multiple variables seperated as commas 
Note this means to type check multiple variables, call like this typeCheck("foo", "bar") not typeCheck(["foo", "bar"])
TODO: for multiple, maybe we really ought to accept a list...
This function will return a tuple, the first entry is a return code, where 0 is success and 1 is failure. When successful, 
the second element will be a dictionary, where the key is the variable name and the value is a dataframe of that variables types
if onlyBool is true, it will check whether or not a variable had the same type and the value will instead be a boolean. True if it kept
its type, false it changed types. If the function failed for some reason, the second tuple element will be a list of possible variable 
names that it can type check. This variable is NOT affected by life cycles, and will ALWAYS show all instances of variables regardless of
the number of life cycles. 

__Example Usage:__
```{Python}
######### Script #########
import provdebug as pvd
prov_explorer = pvd.Explorer("prov_create_test_data/prov.json")
print(prov_explorer.typeCheck("foo"))

######### Output #########
(0, {'foo':    line    varType container  dim        scope
0     1    numeric    vector  [1]  R_GlobalEnv
1     2    numeric    vector  [1]  R_GlobalEnv
2     4    numeric    vector  [1]  R_GlobalEnv
3     6  character    vector  [1]  R_GlobalEnv
4     7  character    vector  [2]  R_GlobalEnv})
```


### errorTrace(stackOverflow = False)

This function searches the provenance for an error message
If one exists, it grabs it and prints the lineage.
If they set stackoverflow to true it will find similar messages on 
stackover flow, print them, and if the user chooses one 
will open that page in on the web browser

### lineage(*args, forward = False)

This function takes variable names as inputs and returns a tuple where the first element is a return code, 0 for success or 1 for failure. The second element of the tuple is 
a list of data frames with the lineage information for the
variables passed. (Lineage being the other variables that
use the inputted variable or were used in the creation of the
inputted variable) If forward is set to true, it will look forward in a script rather than backward. This variable is affecte by life cycles!! When used, it will automatically use the first life cycle for forward, and the last for backward. See getVarLifeCycles for more info on what those are.

__Example Usage:__
```{Python}
######### Script #########
import provdebug as pvd
prov_explorer = pvd.Explorer("prov_create_test_data/prov.json")
print(prov_explorer.lineage("foo"))

######### Output #########
(0, [  scriptNum  startLine              name
0         1          2   foo <- foo * 10
1         1          4  foo <- foo + bar])
```

### fromLine(*args, state = False)

This function returns information about the values of variables
given a line from the program. It can either return all of the
variables referenced on a line, or the state of the entire execution
at the when the line was finished executing.
 
 ### getVarLifeCycles(self, var_name):    
 
This function takes a variable name and returns that variables life cycles. 
Life cycles in this context are groups of instances of a single variable in 
the code where the variable was used to determine its own value. 
For example, the following code has two life cycles. 
```{R}
foo <- 5
foo <- 5 + foo
foo <- 10 * foo
foo <- "hello"
foo <- c(foo, "world")
``` 
The first life cycle is the first 3 instances, and the second life cycle is the last two lines
This function will return a list of dataframes. Each element in the list is a single life cycle, 
so the length of the list is the number of life cycles. Each dataframe is simple a subset of the 
entire data node data frame, except only the rows corresponding to that particular life cycle.

__Example Usage__:
```{Python}
######### Script #########
import provdebug as pvd
prov_explorer = pvd.Explorer("prov_create_test_data/prov.json")
print(prov_explorer.getVarLifeCycles("foo"))

######### Output #########
[   name value                                            valType  type        scope fromEnv hash timestamp location label
d1  foo     5  {"container":"vector", "dimension":[1], "type"...  Data  R_GlobalEnv   False                            d1
d2  foo    50  {"container":"vector", "dimension":[1], "type"...  Data  R_GlobalEnv   False                            d2
d4  foo    57  {"container":"vector", "dimension":[1], "type"...  Data  R_GlobalEnv   False                            d4,    name            value                                            valType  type        scope fromEnv hash timestamp location label
d5  foo          "hello"  {"container":"vector", "dimension":[1], "type"...  Data  R_GlobalEnv   False                            d5
d6  foo  "hello" "world"  {"container":"vector", "dimension":[2], "type"...  Data  R_GlobalEnv   False                            d6]
```
 
 ### getProcedureFromData(data_node):
 
 This function will provide the procedure node where a data node was generated. 
 Requires a data node label and returns a single procedure node row
    
 ### getDataFromProcedure(proc_node):
 
 This function will provide the data node a proc node generated. 
 Requires a proc node label and returns a single dataframe row from data nodes
 
 
    
### \_varsByNode(node):

Originally a helper function, but others may find useful.
This function gathers all variables used in a procedure 
based on the node. Should always be passed a proc node label (p1, p2, etc).
returns a dataframe of data nodes.
In the code foo <- bar + bat, this will return information about bar and bat, NOT foo.
Used by fromLine and getVarsFromCurrentLocation in the Browser
    
    
## Future Features

**Lineage Traversal** 
This will add the functionality of while command-line debugging transtioning to a state where you can debug line by line through the lineage of a single variable. This will help eliminate parts of the code not relevant to a certain outcome. 

**Graphical User Interface**
All of the debugger logic is written to be independent of a single user-interface. While a command-line interface is currently being developed, in the future a GUI may be implemented as well. 
