#!/usr/bin/env python

import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from .DebugRecord import DebugRecord
import provdebug as prov
import readline
import json
import random

# I really don't like global variables/state, but having this as a local variable in run()
# means we'd have to pass it around everywhere.
shouldRecord = False

def recordUserActions(choice, records, info):
    if shouldRecord:
        record = DebugRecord(choice, info)
        records.append(record)

def saveRecords(records):
    recordDicts = [record.writeDict() for record in records]
    encodedRecords = json.dumps(recordDicts)
    # TODO: think of better way to name files
    f = open(f"./debugging-trace-{random.randint(0, 9)}.replay", "w")
    f.write(encodedRecords)
    f.close()

def run():
    # Needed to treat shouldRecord as a global value, and not a local one
    global shouldRecord
    helpText = textwrap.dedent('''\
        Once the interface has started, type help for more information.

        Otherwise, the interactive controls are as follows:
            - n or next: step forward in execution
            - b or back: step backward in execution
            - s or step: step into code block
            - o or out: step out of code block
            - i or info: get current script, line number, and code block
            - v or vars: prints all variables that exist at current location
            - l or lineage [variables]: prints the lineage of each space-separated variable passed to it 
            - p or print [variables]: prints the values of each space-separated variable passed to it
            - so or search: searches a script's error message on Stack Overflow
            - q or quit: quit the debugger
        ''')
    parser = ArgumentParser(description="provdb starts a provenance-based time traveling debugging interface.",
    formatter_class=RawDescriptionHelpFormatter,
    epilog=helpText)
    #Uncomment the following to debug
    '''
    #TO DEBUG
    parser.add_argument('--interactive', action='store_true', default=True)
    (args, rest) = parser.parse_known_args()
    if args.interactive:
        try: readline.read_history_file()
        except: pass
        rest += input("Arguments: ").split(" ")  # get input args
        try: readline.write_history_file()
        except: pass
    '''
    parser.add_argument("-f", "--file", dest="file", required=False,
                        help="Prov.Json file to analyze")

    parser.add_argument("-replay", "--replay-file", dest="file", required=False,
                        help="Prov.Replay file to analyze")

    #TO DEBUG
    #args = parser.parse_args(rest) 
    
    args = parser.parse_args()

    # record of user actions
    userActions = []
    
    browser = prov.Browser(args.file)
    
    print("Welcome to the Multilingual Provenance Debugger, type help for more information")
    browser.stepIn()
    print(browser.getCurrentNodeInfo())
    
    try: readline.read_history_file()
    except: pass

    while(True):
        userInput = input("> ")
        try: readline.write_history_file()
        except: pass

        userChoices = userInput.split(" ")

        userFlag = userChoices[0]

        if(userFlag == "help"):
            recordUserChoice(userFlag, userActions)
            print(helpText)
            continue
        elif(userFlag == "n" or userFlag == "next"):
            recordUserActions(userFlag, userActions, browser.getCurrentNodeInfo())
            browser.nextNode()
        elif(userFlag == "b" or userFlag == "back"):
            recordUserActions(userFlag, userActions, browser.getCurrentNodeInfo())
            
            browser.previousNode()
        elif(userFlag == "s" or userFlag == "step"):
            recordUserActions(userFlag, userActions,  browser.getCurrentNodeInfo())
            browser.stepIn()
        elif(userFlag == "o" or userFlag == "out"):
            recordUserActions(userFlag, userActions,  browser.getCurrentNodeInfo())
            browser.stepOut()
        elif(userFlag == "v" or userFlag == "vars"):
            recordUserActions(userFlag, userActions,  browser.getCurrentNodeInfo())
            print(browser.getVarNamesFromCurrentLocation())
            continue
        elif(userFlag == "i" or userFlag == "info"):
            recordUserActions(userFlag, userActions,  browser.getCurrentNodeInfo())
            print(browser.getCurrentNodeInfo())
            continue
        elif(userFlag == "p" or userFlag == "print"):
            recordUserActions(userFlag, userActions,  browser.getCurrentNodeInfo())
            vars = browser.getVarsFromCurrentLocation()
            varNames = userChoices[1:len(userChoices)]
            if(len(varNames) == 0):
                print("Please enter the name of a variable to see its value")
                continue
            selectedVars = vars[vars["name"].isin(varNames)]
            print(selectedVars)
            continue
        elif(userFlag == "l" or userFlag == "lineage"):
            if(len(userChoices) > 1):
                # TODO: figure out a recording strategy here
                dfs = browser.getVariableLineage(userChoices[1:])

                if(dfs[0] == 1):
                    print("Possible variables to check:")
                    print(dfs[1])
                else:
                    for result in dfs[1]:
                        print(result)
            else:
                print("Please specify a variable or variables to find the lineage for.")
            continue
        elif(userFlag == "so" or userFlag == "search"):
            recordUserActions(userFlag, userActions,  browser.getCurrentNodeInfo())
            code, result = browser.debugger.errorSearch()
            for number, title in enumerate(list(result["title"].values)):
                print(number + 1, title)
            choice = -1
            validInput = False
            while(not validInput):
                choice = input("The number of the page to open (-1 to exit): ")
                try:
                    choice = int(choice)
                    validInput = True
                except:
                    pass
                if(not (1 <= choice <= len(result.index) or choice == -1)):
                    validInput = False
            if(choice != -1):
                browser.debugger.openStackSearch(result, choice)
            continue
        elif(userFlag == "q" or userFlag == "quit"):
            saveRecords(userActions)
            for record in userActions:
                record.prettyPrint()
            break
        elif userFlag == "r" or userFlag == "record":
            if shouldRecord:
                print("This debugging session is already being recorded\n")
            else:
                print("This debugging session is now being recorded\n")
                shouldRecord = True
        elif userFlag == "sr" or userFlag == "stop_record":
            if not shouldRecord:
                print("There is no debugging session being recorded")
            else:
                print("This debugging session has stopped\n")
                saveRecords(userActions)
                userActions = []
                shouldRecord = False

        print(browser.getCurrentNodeInfo())

if __name__ =="__main__":
    run()