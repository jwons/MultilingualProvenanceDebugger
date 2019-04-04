#!/usr/bin/env python

import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import provdebug as pvd 
import readline

def run():
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
            - so or search: searches a scripts error message on Stack Overflow 
            - q or quit: quit the debugger
        ''')
    parser = ArgumentParser(description="provdb starts a provenance-based time traveling debugging interface.",
    formatter_class=RawDescriptionHelpFormatter,
    epilog=helpText)
    #Uncomment the following to debug
    '''
    parser.add_argument('--interactive', action='store_true', default=True)
    (args, rest) = parser.parse_known_args()
    if args.interactive:
        try: readline.read_history_file()
        except: pass
        rest += input("Arguments: ").split(" ")  # get input args
        try: readline.write_history_file()
        except: pass
    '''
    parser.add_argument("-f", "--file", dest="file", required=True,
                        help="Prov.Json file to analyze")

    #args = parser.parse_args(rest) 

    args = parser.parse_args() 


    browser = pvd.ProvBrowser(args.file)
    
    print("Welcome to the Multilingual Provenance Debugger, type help for more information")

    while(True):
        userInput = input(">")

        userChoices = userInput.split(" ")

        userFlag = userChoices[0]

        if(userFlag == "help"):
            print(helpText)
            continue
        elif(userFlag == "n" or userFlag == "next"):
            browser.nextNode()
        elif(userFlag == "b" or userFlag == "back"):
            browser.previousNode()
        elif(userFlag == "s" or userFlag == "step"):
            browser.stepIn()
        elif(userFlag == "o" or userFlag == "out"):
            browser.stepOut()
        elif(userFlag == "v" or userFlag == "vars"):
            print(browser.getVarNamesFromCurrentLocation())
            continue
        elif(userFlag == "i" or userFlag == "info"):
            print(browser.getCurrentNodeInfo())
            continue
        elif(userFlag == "p" or userFlag == "print"):
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
            break

        print(browser.getCurrentNodeInfo())

if __name__ =="__main__":
    run()