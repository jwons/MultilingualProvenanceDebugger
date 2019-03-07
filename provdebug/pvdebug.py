#!/usr/bin/env python

import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import provdebug as pvd 

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
            - q or quit: quit the debugger
        ''')
    parser = ArgumentParser(description="provdb starts a provenance-based time traveling debugging interface.",
    formatter_class=RawDescriptionHelpFormatter,
    epilog=helpText)
    parser.add_argument("-f", "--file", dest="file", required=True,
                        help="Prov.Json file to analyze")

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
        elif(userFlag == "l" or userFlag == "lineage"):
            if(len(userChoices) > 1):
                #TODO figure out how to match input to lineage variables
                dfs = browser.getVariableLineage(userChoices[1])
            else:
                print("Please specify a variable or variables to find the lineage for.")
            continue
        elif(userFlag == "q" or userFlag == "quit"):
            break

        print(browser.getCurrentNodeInfo())

if __name__ =="__main__":
    run()